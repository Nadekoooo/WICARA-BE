from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.modules.accounts.models import UserAccount
from app.modules.ai.client import ai_client
from app.modules.ai.config import get_ai_settings
from app.modules.curriculum.kurikulum_merdeka import canonical_subject_code
from app.modules.curriculum.models import KnowledgeConcept, Subject
from app.modules.curriculum.seed import seed_curriculum
from app.modules.learning.models import AssessmentSession, LearningGoal
from app.modules.learning_goal_resolution.candidate_retriever import (
    CandidateConceptRetriever,
    ConceptCandidate,
    score_to_confidence,
)
from app.modules.learning_goal_resolution.models import LearningGoalResolution
from app.modules.learning_goal_resolution.level_context import (
    grade_relation_for_concept,
    level_note_for_relation,
)
from app.modules.learning_goal_resolution.prompt_builder import (
    PROMPT_VERSION,
    build_goal_resolution_prompt,
)
from app.modules.learning_goal_resolution.schemas import (
    ActiveGoalRead,
    ActiveLearningGoalResponse,
    ArchiveGoalResponse,
    CancelGoalResponse,
    ConceptCandidateRead,
    ConfirmLearningGoalResponse,
    ResolveLearningGoalResponse,
)
from app.modules.tracks.path_builder import TrackBuilderService


ACTIVE_GOAL_STATUSES = {"confirmed", "pretest_in_progress", "diagnosed", "in_progress"}
INACTIVE_GOAL_STATUSES = {"completed", "cancelled", "archived"}
EXACT_MATCH_CONFIDENCE_THRESHOLD = 0.75


class ActiveLearningGoalExists(Exception):
    def __init__(self, active_goal: ActiveGoalRead) -> None:
        self.active_goal = active_goal


@dataclass(frozen=True)
class ScopeAttempt:
    scope: str
    scope_reason: str
    candidates: list[ConceptCandidate]
    llm_result: dict[str, Any]
    selected: ConceptCandidate
    alternatives: list[ConceptCandidate]
    confidence: float
    status: str


class GoalResolverService:
    def __init__(
        self,
        *,
        retriever: CandidateConceptRetriever | None = None,
        track_builder: TrackBuilderService | None = None,
    ) -> None:
        self.retriever = retriever or CandidateConceptRetriever()
        self.track_builder = track_builder or TrackBuilderService()

    async def resolve(
        self,
        session: Session,
        *,
        user: UserAccount,
        raw_query: str,
        subject_code: str | None,
        education_level: str | None,
        grade_level: str | None,
        language: str,
    ) -> ResolveLearningGoalResponse:
        _ensure_curriculum(session)
        explicit_subject_code = subject_code
        attempt = await self._resolve_progressively(
            session,
            raw_query=raw_query,
            subject_code=explicit_subject_code,
            education_level=education_level,
            grade_level=grade_level,
            language=language,
            allow_cross_subject=explicit_subject_code is None,
        )
        if attempt is None:
            clarification = _localized_message(
                language,
                id_text="Aku belum menemukan materi yang cocok. Bisa jelaskan lebih spesifik?",
                en_text="I could not find a matching concept yet. Can you make the goal more specific?",
            )
            resolution = LearningGoalResolution(
                user_id=user.id,
                raw_query=raw_query.strip(),
                subject_code=subject_code or "",
                education_level=education_level or "",
                grade_level=grade_level or "",
                language=language,
                status="needs_clarification",
                llm_provider="none",
                llm_model="none",
                prompt_version=PROMPT_VERSION,
                llm_response_json={"status": "needs_clarification"},
            )
            session.add(resolution)
            session.commit()
            return ResolveLearningGoalResponse(
                resolution_id=resolution.id,
                status=resolution.status,
                confidence=0.0,
                clarification_question=clarification,
                search_scope="no_match",
                search_scope_reason="No scope returned any candidate.",
            )

        selected = attempt.selected
        candidates = attempt.candidates
        alternatives = attempt.alternatives
        confidence = attempt.confidence
        status = attempt.status
        llm_result = attempt.llm_result
        resolution = LearningGoalResolution(
            user_id=user.id,
            raw_query=raw_query.strip(),
            subject_code=explicit_subject_code or (selected.concept.subject.code if selected.concept.subject else ""),
            education_level=education_level or "",
            grade_level=grade_level or "",
            language=language,
            suggested_concept_id=selected.concept.id if status == "needs_confirmation" else None,
            confidence=confidence,
            alternatives_json=[candidate.snapshot() for candidate in alternatives],
            candidate_snapshot_json=[candidate.snapshot() for candidate in candidates],
            llm_response_json=llm_result,
            status=status,
            llm_provider=str(llm_result.get("provider", "deterministic_fallback")),
            llm_model=str(llm_result.get("model", "deterministic_fallback")),
            prompt_version=PROMPT_VERSION,
        )
        session.add(resolution)
        session.commit()

        return ResolveLearningGoalResponse(
            resolution_id=resolution.id,
            status=resolution.status,
            suggested_concept=(
                _concept_to_read(
                    selected,
                    confidence=confidence,
                    education_level=education_level,
                    grade_level=grade_level,
                    language=language,
                )
                if resolution.suggested_concept_id
                else None
            ),
            confidence=confidence,
            alternatives=[
                _concept_to_read(
                    candidate,
                    confidence=score_to_confidence(candidate.score),
                    education_level=education_level,
                    grade_level=grade_level,
                    language=language,
                )
                for candidate in alternatives
            ],
            clarification_question=(
                _localized_message(
                    language,
                    id_text=f"Benar kamu mau belajar {selected.concept.title}?",
                    en_text=f"Do you want to learn {selected.concept.title}?",
                )
                if status == "needs_confirmation"
                else _clarification_from_candidates(language=language, candidates=alternatives)
            ),
            search_scope=attempt.scope,
            search_scope_reason=attempt.scope_reason,
            graph_focus=_graph_focus(selected=selected, alternatives=alternatives),
            can_expand_scope=_can_expand_scope(
                attempt.scope,
                allow_cross_subject=explicit_subject_code is None,
            ),
            candidate_debug=_candidate_debug(candidates, scope=attempt.scope),
        )

    async def reprompt(
        self,
        session: Session,
        *,
        user: UserAccount,
        resolution_id: UUID,
        raw_query: str,
    ) -> ResolveLearningGoalResponse | None:
        previous = session.scalar(
            select(LearningGoalResolution).where(
                LearningGoalResolution.id == resolution_id,
                LearningGoalResolution.user_id == user.id,
            )
        )
        if previous is None:
            return None
        previous.status = "rejected"
        return await self.resolve(
            session,
            user=user,
            raw_query=raw_query,
            subject_code=previous.subject_code or None,
            education_level=previous.education_level or None,
            grade_level=previous.grade_level or None,
            language=previous.language or "id",
        )

    def select_concept(
        self,
        session: Session,
        *,
        user: UserAccount,
        resolution_id: UUID,
        concept_id: UUID | None,
        concept_code: str | None,
    ) -> ResolveLearningGoalResponse | None:
        resolution = session.scalar(
            select(LearningGoalResolution).where(
                LearningGoalResolution.id == resolution_id,
                LearningGoalResolution.user_id == user.id,
            )
        )
        if resolution is None:
            return None
        if concept_id is None and not (concept_code or "").strip():
            raise ValueError("Select either concept_id or concept_code.")

        snapshots = _resolution_candidate_snapshots(resolution)
        selected_snapshot = _find_candidate_snapshot(
            snapshots,
            concept_id=concept_id,
            concept_code=concept_code,
        )
        concept = (
            _concept_from_candidate_snapshot(session, selected_snapshot)
            if selected_snapshot is not None
            else _concept_from_selection(session, concept_id=concept_id, concept_code=concept_code)
        )
        if concept is None:
            raise ValueError("Selected concept was not found.")
        if not _concept_allowed_for_resolution(concept, resolution=resolution):
            raise ValueError("Selected concept is outside the locked subject for this resolution.")
        if selected_snapshot is None:
            selected_snapshot = _snapshot_from_concept(concept, confidence=0.99)

        selected_confidence = _snapshot_confidence(selected_snapshot)
        selected_candidate = _candidate_from_concept_snapshot(concept, selected_snapshot)
        alternatives = [
            candidate
            for snapshot in snapshots
            if (candidate := _candidate_from_snapshot(session, snapshot)) is not None
            and candidate.concept.id != concept.id
        ][:4]

        resolution.suggested_concept_id = concept.id
        resolution.confidence = selected_confidence
        resolution.status = "needs_confirmation"
        resolution.alternatives_json = [candidate.snapshot() for candidate in alternatives]
        resolution.llm_response_json = {
            **(resolution.llm_response_json or {}),
            "manual_candidate_selection": {
                "concept_id": str(concept.id),
                "concept_code": concept.code,
                "selected_at": datetime.now(UTC).isoformat(),
            },
        }
        session.commit()

        return ResolveLearningGoalResponse(
            resolution_id=resolution.id,
            status=resolution.status,
            suggested_concept=_concept_to_read(
                selected_candidate,
                confidence=selected_confidence,
                education_level=resolution.education_level or None,
                grade_level=resolution.grade_level or None,
                language=resolution.language or "id",
            ),
            confidence=selected_confidence,
            alternatives=[
                _concept_to_read(
                    candidate,
                    confidence=score_to_confidence(candidate.score),
                    education_level=resolution.education_level or None,
                    grade_level=resolution.grade_level or None,
                    language=resolution.language or "id",
                )
                for candidate in alternatives
            ],
            clarification_question=_localized_message(
                resolution.language or "id",
                id_text=f"Benar kamu mau belajar {concept.title}?",
                en_text=f"Do you want to learn {concept.title}?",
            ),
            search_scope=str((resolution.llm_response_json or {}).get("scope") or "manual_candidate_selection"),
            search_scope_reason=_localized_message(
                resolution.language or "id",
                id_text="Kandidat dipilih langsung dari hasil rekomendasi sebelumnya.",
                en_text="Candidate selected directly from the previous recommendation set.",
            ),
            graph_focus=_graph_focus(selected=selected_candidate, alternatives=alternatives),
            can_expand_scope=False,
            candidate_debug=_candidate_debug([selected_candidate, *alternatives], scope="manual_candidate_selection"),
        )

    def confirm(
        self,
        session: Session,
        *,
        user: UserAccount,
        resolution_id: UUID,
    ) -> ConfirmLearningGoalResponse | None:
        resolution = session.scalar(
            select(LearningGoalResolution).where(
                LearningGoalResolution.id == resolution_id,
                LearningGoalResolution.user_id == user.id,
            )
        )
        if resolution is None:
            return None
        if resolution.suggested_concept_id is None:
            raise ValueError("Resolution has no suggested concept to confirm.")
        active = self.get_active_goal(session, user=user)
        if active.goal is not None:
            raise ActiveLearningGoalExists(active.goal)

        concept = session.get(KnowledgeConcept, resolution.suggested_concept_id)
        if concept is None:
            raise ValueError("Suggested concept was not found.")
        subject = session.get(Subject, concept.subject_id)
        goal = LearningGoal(
            user_id=user.id,
            subject_id=concept.subject_id,
            target_concept_id=concept.id,
            resolution_id=resolution.id,
            raw_topic=resolution.raw_query,
            normalized_topic=concept.title,
            status="confirmed",
            metadata_json={
                "source": "goal_resolution",
                "resolution_id": str(resolution.id),
                "subject_code": subject.code if subject else resolution.subject_code,
            },
        )
        resolution.status = "confirmed"
        resolution.confirmed_at = datetime.now(UTC)
        session.add(goal)
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            active_after_race = self.get_active_goal(session, user=user)
            if active_after_race.goal is not None:
                raise ActiveLearningGoalExists(active_after_race.goal) from exc
            raise
        return ConfirmLearningGoalResponse(
            learning_goal_id=goal.id,
            status=goal.status,
            target_concept=_concept_to_read(
                ConceptCandidate(concept=concept, score=resolution.confidence),
                confidence=resolution.confidence,
            ),
        )

    def get_active_goal(
        self,
        session: Session,
        *,
        user: UserAccount,
    ) -> ActiveLearningGoalResponse:
        goal = session.scalar(
            select(LearningGoal)
            .where(LearningGoal.user_id == user.id, LearningGoal.status.in_(ACTIVE_GOAL_STATUSES))
            .options(selectinload(LearningGoal.track), selectinload(LearningGoal.assessment_sessions))
            .order_by(LearningGoal.created_at.desc())
        )
        return ActiveLearningGoalResponse(
            has_active_goal=goal is not None,
            goal=_active_goal_to_read(session, goal) if goal else None,
        )

    def cancel_goal(
        self,
        session: Session,
        *,
        user: UserAccount,
        learning_goal_id: UUID,
    ) -> CancelGoalResponse | None:
        goal = session.scalar(
            select(LearningGoal).where(LearningGoal.id == learning_goal_id, LearningGoal.user_id == user.id)
        )
        if goal is None:
            return None
        abandoned: list[UUID] = []
        for assessment in session.scalars(
            select(AssessmentSession).where(
                AssessmentSession.learning_goal_id == goal.id,
                AssessmentSession.session_type == "pretest",
                AssessmentSession.status.in_({"active", "awaiting_answer"}),
            )
        ):
            assessment.status = "cancelled"
            abandoned.append(assessment.id)
        goal.status = "cancelled"
        goal.cancelled_at = datetime.now(UTC)
        session.commit()
        return CancelGoalResponse(
            learning_goal_id=goal.id,
            status=goal.status,
            abandoned_pretest_session_ids=abandoned,
        )

    def archive_goal(
        self,
        session: Session,
        *,
        user: UserAccount,
        learning_goal_id: UUID,
    ) -> ArchiveGoalResponse | None:
        goal = session.scalar(
            select(LearningGoal).where(LearningGoal.id == learning_goal_id, LearningGoal.user_id == user.id)
        )
        if goal is None:
            return None
        if goal.status not in INACTIVE_GOAL_STATUSES:
            raise ValueError("Only completed or cancelled goals can be archived.")
        goal.status = "archived"
        goal.archived_at = datetime.now(UTC)
        session.commit()
        return ArchiveGoalResponse(learning_goal_id=goal.id, status=goal.status)

    def search_materials(
        self,
        session: Session,
        *,
        query: str,
        subject_code: str | None,
        user: UserAccount,
    ) -> list[ConceptCandidateRead]:
        _ensure_curriculum(session)
        candidates = self.retriever.search(
            session,
            query=query,
            subject_code=subject_code,
            education_level=user.learner_profile.education_level if user.learner_profile else None,
            grade_level=user.learner_profile.grade_level if user.learner_profile else None,
            limit=20,
        )
        return [
            _concept_to_read(
                candidate,
                confidence=score_to_confidence(candidate.score),
                education_level=user.learner_profile.education_level if user.learner_profile else None,
                grade_level=user.learner_profile.grade_level if user.learner_profile else None,
                language=user.learner_profile.preferred_language if user.learner_profile else "id",
            )
            for candidate in candidates
        ]

    async def _resolve_progressively(
        self,
        session: Session,
        *,
        raw_query: str,
        subject_code: str | None,
        education_level: str | None,
        grade_level: str | None,
        language: str,
        allow_cross_subject: bool,
    ) -> ScopeAttempt | None:
        best_attempt: ScopeAttempt | None = None
        for scope in _progressive_scopes(
            subject_code=subject_code,
            language=language,
            allow_cross_subject=allow_cross_subject,
        ):
            candidates = self.retriever.search(
                session,
                query=raw_query,
                subject_code=scope["subject_code"],
                education_level=education_level,
                grade_level=grade_level,
                grade_scope=scope["grade_scope"],
                include_context_fallback=True,
                limit=_candidate_limit_for_scope(str(scope["name"])),
            )
            if not candidates:
                continue
            llm_result = await self._resolve_with_ai(raw_query=raw_query, candidates=candidates)
            llm_status = _normalized_llm_status(llm_result)
            selected = _validated_candidate(llm_result, candidates)
            fallback_candidate = selected or candidates[0]
            confidence = _coerce_confidence(
                llm_result.get("confidence"),
                fallback=fallback_candidate.score if selected else 0.0,
            )
            alternatives = _validated_alternatives(llm_result, candidates, selected=selected)

            if llm_status == "exact_match" and selected is not None and confidence >= EXACT_MATCH_CONFIDENCE_THRESHOLD:
                status = "needs_confirmation"
            elif llm_status == "ambiguous":
                status = "needs_clarification"
            elif llm_status == "exact_match":
                status = "no_match"
            else:
                status = "no_match"

            if not alternatives:
                alternatives = [
                    candidate
                    for candidate in candidates
                    if selected is None or candidate.concept.id != selected.concept.id
                ][:4]
            attempt = ScopeAttempt(
                scope=str(scope["name"]),
                scope_reason=str(scope["reason"]),
                candidates=candidates,
                llm_result={
                    **llm_result,
                    "scope": scope["name"],
                    "scope_reason": scope["reason"],
                    "candidate_count": len(candidates),
                    "backend_interpreted_status": status,
                },
                selected=fallback_candidate,
                alternatives=alternatives,
                confidence=confidence,
                status="needs_confirmation" if status == "needs_confirmation" else "needs_clarification",
            )
            if _attempt_rank(attempt) > _attempt_rank(best_attempt):
                best_attempt = attempt
            if status == "needs_confirmation":
                return attempt
        return best_attempt

    async def _resolve_with_ai(
        self,
        *,
        raw_query: str,
        candidates: list[ConceptCandidate],
    ) -> dict[str, Any]:
        settings = get_ai_settings()
        if not settings.gemini_api_key.strip():
            top = candidates[0]
            confidence = score_to_confidence(top.score)
            status = "exact_match" if confidence >= EXACT_MATCH_CONFIDENCE_THRESHOLD else "no_match"
            return {
                "status": status,
                "selected_concept_code": top.concept.code if status == "exact_match" else None,
                "confidence": confidence,
                "alternatives": [candidate.concept.code for candidate in candidates[1:4]],
                "reason": "Deterministic fallback used because Gemini is not configured.",
                "should_expand_scope": status == "no_match",
                "clarification_question": None if status == "exact_match" else "Coba tulis goal belajar yang lebih spesifik.",
                "provider": "deterministic_fallback",
                "model": "candidate_score",
            }
        prompt = build_goal_resolution_prompt(raw_query=raw_query, candidates=candidates)
        try:
            response = await ai_client.generate(
                system_instruction="Return valid JSON only.",
                user_instruction=prompt,
                params={"temperature": 0.0, "response_mime_type": "application/json"},
            )
            payload = json.loads(response.text)
            payload["provider"] = response.provider
            payload["model"] = response.model
            return payload
        except Exception as exc:
            top = candidates[0]
            confidence = score_to_confidence(top.score)
            status = "exact_match" if confidence >= EXACT_MATCH_CONFIDENCE_THRESHOLD else "no_match"
            return {
                "status": status,
                "selected_concept_code": top.concept.code if status == "exact_match" else None,
                "confidence": confidence,
                "alternatives": [candidate.concept.code for candidate in candidates[1:4]],
                "reason": "Deterministic fallback used because LLM resolution failed.",
                "should_expand_scope": status == "no_match",
                "clarification_question": None if status == "exact_match" else "Coba tulis goal belajar yang lebih spesifik.",
                "provider": "deterministic_fallback",
                "model": "candidate_score",
                "fallback_reason": str(exc),
            }


def _validated_candidate(
    llm_result: dict[str, Any],
    candidates: list[ConceptCandidate],
) -> ConceptCandidate | None:
    selected_code = str(
        llm_result.get("selected_concept_code") or llm_result.get("concept_code") or ""
    ).strip()
    if not selected_code:
        return None
    return next((candidate for candidate in candidates if candidate.concept.code == selected_code), None)


def _validated_alternatives(
    llm_result: dict[str, Any],
    candidates: list[ConceptCandidate],
    *,
    selected: ConceptCandidate | None,
) -> list[ConceptCandidate]:
    raw_alternatives = llm_result.get("alternatives", [])
    if not isinstance(raw_alternatives, list):
        return []
    by_code = {candidate.concept.code: candidate for candidate in candidates}
    alternatives: list[ConceptCandidate] = []
    for raw_code in raw_alternatives:
        code = str(raw_code or "").strip()
        candidate = by_code.get(code)
        if candidate is None:
            continue
        if selected is not None and candidate.concept.id == selected.concept.id:
            continue
        if any(item.concept.id == candidate.concept.id for item in alternatives):
            continue
        alternatives.append(candidate)
        if len(alternatives) >= 4:
            break
    return alternatives


def _normalized_llm_status(llm_result: dict[str, Any]) -> str:
    status = str(llm_result.get("status") or "").strip().lower()
    if status in {"exact_match", "needs_confirmation", "confirmed", "match"}:
        return "exact_match"
    if status in {"ambiguous", "needs_clarification", "clarification"}:
        return "ambiguous"
    return "no_match"


def _resolution_candidate_snapshots(resolution: LearningGoalResolution) -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    for raw_snapshot in [
        *(resolution.candidate_snapshot_json or []),
        *(resolution.alternatives_json or []),
    ]:
        if not isinstance(raw_snapshot, dict):
            continue
        key = str(raw_snapshot.get("concept_id") or raw_snapshot.get("concept_code") or "").strip()
        if not key:
            continue
        if any(
            str(item.get("concept_id") or item.get("concept_code")) == key
            for item in snapshots
        ):
            continue
        snapshots.append(raw_snapshot)
    return snapshots


def _find_candidate_snapshot(
    snapshots: list[dict[str, Any]],
    *,
    concept_id: UUID | None,
    concept_code: str | None,
) -> dict[str, Any] | None:
    target_id = str(concept_id) if concept_id is not None else ""
    target_code = (concept_code or "").strip()
    for snapshot in snapshots:
        if target_id and str(snapshot.get("concept_id") or "") == target_id:
            return snapshot
        if target_code and str(snapshot.get("concept_code") or "") == target_code:
            return snapshot
    return None


def _concept_from_candidate_snapshot(
    session: Session,
    snapshot: dict[str, Any],
) -> KnowledgeConcept | None:
    raw_id = str(snapshot.get("concept_id") or "").strip()
    if raw_id:
        try:
            concept = session.get(KnowledgeConcept, UUID(raw_id))
            if concept is not None:
                return concept
        except ValueError:
            pass
    code = str(snapshot.get("concept_code") or "").strip()
    if not code:
        return None
    return session.scalar(select(KnowledgeConcept).where(KnowledgeConcept.code == code))


def _concept_from_selection(
    session: Session,
    *,
    concept_id: UUID | None,
    concept_code: str | None,
) -> KnowledgeConcept | None:
    if concept_id is not None:
        concept = session.get(KnowledgeConcept, concept_id)
        if concept is not None:
            return concept
    code = (concept_code or "").strip()
    if not code:
        return None
    return session.scalar(select(KnowledgeConcept).where(KnowledgeConcept.code == code))


def _concept_allowed_for_resolution(
    concept: KnowledgeConcept,
    *,
    resolution: LearningGoalResolution,
) -> bool:
    locked_subject = (resolution.subject_code or "").strip()
    if not locked_subject:
        return True
    subject = concept.subject
    return subject is not None and subject.code == canonical_subject_code(locked_subject)


def _snapshot_from_concept(concept: KnowledgeConcept, *, confidence: float) -> dict[str, Any]:
    subject = concept.subject
    return {
        "concept_id": str(concept.id),
        "concept_code": concept.code,
        "title": concept.title,
        "description": concept.description,
        "subject_code": subject.code if subject else "",
        "subject": subject.name if subject else "",
        "grade_band": concept.grade_band,
        "aliases": [],
        "score": 18.0 * confidence,
        "confidence": confidence,
        "matched_signals": ["manual_selection"],
    }


def _candidate_from_snapshot(
    session: Session,
    snapshot: dict[str, Any],
) -> ConceptCandidate | None:
    concept = _concept_from_candidate_snapshot(session, snapshot)
    if concept is None:
        return None
    return _candidate_from_concept_snapshot(concept, snapshot)


def _candidate_from_concept_snapshot(
    concept: KnowledgeConcept,
    snapshot: dict[str, Any],
) -> ConceptCandidate:
    return ConceptCandidate(
        concept=concept,
        score=_snapshot_score(snapshot),
        matched_signals=tuple(str(item) for item in snapshot.get("matched_signals", []) if str(item).strip())
        if isinstance(snapshot.get("matched_signals"), list)
        else (),
        aliases=tuple(str(item) for item in snapshot.get("aliases", []) if str(item).strip())
        if isinstance(snapshot.get("aliases"), list)
        else (),
    )


def _snapshot_confidence(snapshot: dict[str, Any]) -> float:
    value = snapshot.get("confidence")
    try:
        return max(0.0, min(0.99, float(value)))
    except (TypeError, ValueError):
        return score_to_confidence(_snapshot_score(snapshot))


def _snapshot_score(snapshot: dict[str, Any]) -> float:
    try:
        return float(snapshot.get("score") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _coerce_confidence(value: Any, *, fallback: float) -> float:
    if value is None:
        return score_to_confidence(float(fallback or 0.0))
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return score_to_confidence(float(fallback or 0.0))
    if confidence > 1.0:
        return score_to_confidence(confidence)
    return max(0.0, min(0.99, confidence))


def _localized_message(language: str, *, id_text: str, en_text: str) -> str:
    normalized = (language or "").strip().lower()
    if normalized in {"id", "indonesian", "bahasa indonesia"} or "indo" in normalized:
        return id_text
    return en_text


def _concept_to_read(
    candidate: ConceptCandidate,
    *,
    confidence: float | None = None,
    education_level: str | None = None,
    grade_level: str | None = None,
    language: str = "",
) -> ConceptCandidateRead:
    concept = candidate.concept
    subject = concept.subject
    relation = grade_relation_for_concept(
        concept,
        education_level=education_level,
        grade_level=grade_level,
    )
    return ConceptCandidateRead(
        concept_id=concept.id,
        concept_code=concept.code,
        title=concept.title,
        description=concept.description,
        subject_code=subject.code if subject else "",
        subject=subject.name if subject else "",
        grade_band=concept.grade_band,
        grade_relation=relation,
        level_note=level_note_for_relation(relation, language=language),
        confidence=round(
            float(confidence if confidence is not None else score_to_confidence(candidate.score)),
            3,
        ),
        aliases=list(candidate.aliases),
        matched_signals=list(candidate.matched_signals),
    )


def _is_ambiguous(candidates: list[ConceptCandidate]) -> bool:
    if len(candidates) < 2:
        return False
    top, runner_up = candidates[0], candidates[1]
    if top.score <= 0:
        return False
    margin_ratio = (top.score - runner_up.score) / max(top.score, 1.0)
    return margin_ratio < 0.12


def _clarification_from_candidates(*, language: str, candidates: list[ConceptCandidate]) -> str:
    titles = [candidate.concept.title for candidate in candidates[:3]]
    if not titles:
        return _localized_message(
            language,
            id_text="Maksud kamu materi yang mana? Coba tulis lebih spesifik.",
            en_text="Which material did you mean? Try a more specific query.",
        )
    options = ", ".join(titles)
    return _localized_message(
        language,
        id_text=f"Maksud kamu yang mana: {options}?",
        en_text=f"Which one did you mean: {options}?",
    )


def _candidate_debug(candidates: list[ConceptCandidate], *, scope: str) -> list[dict[str, Any]]:
    return [
        {
            "scope": scope,
            "concept_code": candidate.concept.code,
            "title": candidate.concept.title,
            "score": round(candidate.score, 3),
            "confidence": score_to_confidence(candidate.score),
            "matched_signals": list(candidate.matched_signals),
            "aliases": list(candidate.aliases[:8]),
        }
        for candidate in candidates[:12]
    ]


def _progressive_scopes(
    *,
    subject_code: str | None,
    language: str,
    allow_cross_subject: bool,
) -> list[dict[str, str | None]]:
    is_id = _is_indonesian_language(language)
    scopes: list[dict[str, str | None]] = [
        {
            "name": "current_grade",
            "subject_code": subject_code,
            "grade_scope": "current_grade",
            "reason": (
                "Mencari node di level kelas saat ini."
                if is_id
                else "Searching nodes at the learner's current grade level."
            ),
        },
        {
            "name": "nearby_grade",
            "subject_code": subject_code,
            "grade_scope": "nearby_grade",
            "reason": (
                "Memperluas ke level sekitar karena kandidat awal belum cukup yakin."
                if is_id
                else "Expanding to nearby grade levels because the first scope was not confident enough."
            ),
        },
    ]
    if subject_code:
        scopes.insert(
            2,
            {
                "name": "same_subject_all_grades",
                "subject_code": subject_code,
                "grade_scope": "all",
                "reason": (
                    "Mencari semua grade di subject yang sama."
                    if is_id
                    else "Searching all grades in the same subject."
                ),
            },
        )
    if allow_cross_subject:
        scopes.append(
            {
                "name": "all_subjects_all_grades",
                "subject_code": None,
                "grade_scope": "all",
                "reason": (
                    "Mencari semua subject dan semua grade karena belum ada subject yang dikunci."
                    if is_id
                    else "Searching all subjects and all grades because no subject was locked."
                ),
            }
        )
    seen: set[tuple[str, str | None, str | None]] = set()
    unique_scopes: list[dict[str, str | None]] = []
    for scope in scopes:
        key = (str(scope["name"]), scope["subject_code"], scope["grade_scope"])
        if key in seen:
            continue
        seen.add(key)
        unique_scopes.append(scope)
    return unique_scopes


def _attempt_rank(attempt: ScopeAttempt | None) -> float:
    if attempt is None:
        return -1.0
    status_bonus = 2.0 if attempt.status == "needs_confirmation" else 0.0
    return status_bonus + attempt.confidence + score_to_confidence(attempt.selected.score)


def _candidate_limit_for_scope(scope_name: str) -> int:
    if scope_name == "all_subjects_all_grades":
        return 500
    if scope_name == "same_subject_all_grades":
        return 240
    return 180


def _can_expand_scope(scope_name: str, *, allow_cross_subject: bool) -> bool:
    if scope_name in {"current_grade", "nearby_grade"}:
        return True
    if scope_name == "same_subject_all_grades":
        return allow_cross_subject
    return False


def _graph_focus(*, selected: ConceptCandidate, alternatives: list[ConceptCandidate]) -> dict[str, Any]:
    subject = selected.concept.subject
    codes = [selected.concept.code]
    codes.extend(candidate.concept.code for candidate in alternatives)
    unique_codes = list(dict.fromkeys(code for code in codes if code))
    return {
        "subject_code": subject.code if subject else "",
        "highlight_concept_codes": unique_codes[:8],
        "selected_concept_code": selected.concept.code,
    }


def _is_indonesian_language(language: str) -> bool:
    normalized = (language or "").strip().lower()
    return normalized in {"id", "indonesian", "bahasa indonesia"} or "indo" in normalized


def _active_goal_to_read(session: Session, goal: LearningGoal) -> ActiveGoalRead:
    concept = session.get(KnowledgeConcept, goal.target_concept_id) if goal.target_concept_id else None
    subject = session.get(Subject, concept.subject_id) if concept else None
    pretest = next(
        (
            assessment
            for assessment in goal.assessment_sessions
            if assessment.session_type == "pretest" and assessment.status in {"active", "awaiting_answer"}
        ),
        None,
    )
    next_action = {
        "confirmed": "start_pretest",
        "pretest_in_progress": "continue_pretest",
        "diagnosed": "choose_path",
        "in_progress": "continue_learning",
    }.get(goal.status, "view_progress")
    return ActiveGoalRead(
        id=goal.id,
        status=goal.status,
        raw_topic=goal.raw_topic,
        target_concept=ConceptCandidateRead(
            concept_id=concept.id,
            concept_code=concept.code,
            title=concept.title,
            description=concept.description,
            subject_code=subject.code if subject else "",
            subject=subject.name if subject else "",
            grade_band=concept.grade_band,
            confidence=None,
        )
        if concept
        else None,
        pretest_session_id=pretest.id if pretest else None,
        track_id=goal.track.id if goal.track else None,
        next_action=next_action,
    )


def _ensure_curriculum(session: Session) -> None:
    if session.scalar(select(Subject.id).limit(1)) is None:
        seed_curriculum(session)

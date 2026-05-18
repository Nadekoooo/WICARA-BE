from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.language import normalize_language_code, preferred_language_code
from app.modules.accounts.models import UserAccount
from app.modules.curriculum.kurikulum_merdeka import canonical_subject_code
from app.modules.curriculum.models import KnowledgeConcept, Subject
from app.modules.learning.models import (
    AssessmentAttempt,
    AssessmentQuestion,
    AssessmentSession,
    LearnerConceptState,
    LearningTrack,
    TrackModule,
)
from app.modules.question_bank.models import (
    QuestionBankImportRun,
    QuestionBankItem,
    QuestionBankOption,
)

SUPPORTED_ASSESSMENT_TYPES = {"pretest", "daily_quiz", "posttest", "workspace_quiz"}
SUPPORTED_DIFFICULTIES = {"easy", "medium", "hard"}
SUPPORTED_STATUSES = {"draft", "reviewed", "active", "retired"}
DAILY_SELECTOR_VERSION = "daily_ebbinghaus_v1"
DAILY_STALE_REVIEW_MIN_DAYS = 2
DAILY_LOW_MASTERY_THRESHOLD = 0.55


@dataclass(frozen=True)
class ImportSummary:
    files_processed: int
    imported_count: int
    skipped_count: int
    failed_count: int
    errors: list[dict[str, Any]]


@dataclass(frozen=True)
class LearnerStep:
    subject: Subject
    education_level: str
    preferred_language: str
    active_track_id: UUID | None
    active_module_id: UUID | None
    active_concept_id: UUID | None
    due_states: list[LearnerConceptState]
    weak_states: list[LearnerConceptState]


@dataclass(frozen=True)
class SelectedQuestion:
    item: QuestionBankItem
    slot: str
    reason: str
    metadata_json: dict[str, Any]


@dataclass(frozen=True)
class _EbbinghausCandidate:
    state: LearnerConceptState
    slot: str
    reason: str
    priority_score: float
    estimated_retention: float
    forgetting_risk: float
    elapsed_days: float
    scheduled_overdue_days: float


def ensure_question_bank_seeded(
    session: Session,
    *,
    commit: bool = True,
    preferred_language: str | None = None,
) -> None:
    """Import seed JSON when the bank or the requested language is missing."""
    existing = session.scalar(select(QuestionBankItem.id).limit(1))
    if existing is None:
        import_seed_directory(session, strict=False, commit=commit)
        return

    language = normalize_language_code(preferred_language, fallback="")
    if language and session.scalar(
        select(QuestionBankItem.id).where(QuestionBankItem.language == language).limit(1)
    ) is None:
        import_seed_directory(session, strict=False, commit=commit)


def import_seed_directory(
    session: Session,
    *,
    seeds_dir: Path | None = None,
    strict: bool = False,
    commit: bool = True,
) -> ImportSummary:
    seeds_path = seeds_dir or default_seeds_dir()
    files = sorted(seeds_path.glob("*.json"))
    imported_total = 0
    skipped_total = 0
    failed_total = 0
    errors: list[dict[str, Any]] = []

    for path in files:
        summary = import_seed_file(session, path=path, strict=strict)
        imported_total += summary.imported_count
        skipped_total += summary.skipped_count
        failed_total += summary.failed_count
        errors.extend(summary.errors_json)

    if commit:
        session.commit()
    return ImportSummary(
        files_processed=len(files),
        imported_count=imported_total,
        skipped_count=skipped_total,
        failed_count=failed_total,
        errors=errors,
    )


def import_seed_file(
    session: Session,
    *,
    path: Path,
    strict: bool,
) -> QuestionBankImportRun:
    raw = path.read_text(encoding="utf-8")
    source_hash = _sha256(raw)
    run = QuestionBankImportRun(
        source_path=str(path),
        source_hash=source_hash,
        strict_mode=strict,
        errors_json=[],
    )
    session.add(run)
    session.flush()

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        run.failed_count = 1
        run.errors_json = [{"file": path.name, "error": f"invalid_json: {exc}"}]
        run.completed_at = datetime.now(UTC)
        if strict:
            raise ValueError(run.errors_json[0]["error"]) from exc
        return run

    file_errors = validate_seed_payload(payload, source_name=path.name)
    if file_errors:
        run.failed_count = len(file_errors)
        run.errors_json = file_errors
        run.completed_at = datetime.now(UTC)
        if strict:
            raise ValueError(f"Seed validation failed for {path.name}: {file_errors[:3]}")
        return run

    subject_code = canonical_subject_code(str(payload["subject_code"]))
    subject = session.scalar(select(Subject).where(Subject.code == subject_code))
    if subject is None:
        error = {"file": path.name, "error": f"unknown_subject:{subject_code}"}
        run.failed_count = 1
        run.errors_json = [error]
        run.completed_at = datetime.now(UTC)
        if strict:
            raise ValueError(error["error"])
        return run

    version = str(payload["version"])
    source = str(payload["source"])
    item_errors: list[dict[str, Any]] = []
    imported = 0
    skipped = 0

    for item_payload in payload["items"]:
        concept_code = str(item_payload["concept_code"]).strip()
        concept = _find_concept_for_seed(session, subject=subject, concept_code=concept_code)
        if concept is None and strict:
            item_errors.append(
                {
                    "file": path.name,
                    "item_id": item_payload["id"],
                    "error": f"unknown_concept:{concept_code}",
                }
            )
            continue

        content_hash = _sha256(json.dumps(item_payload, sort_keys=True, ensure_ascii=True))
        existing = session.scalar(
            select(QuestionBankItem)
            .where(QuestionBankItem.external_id == str(item_payload["id"]))
            .options(selectinload(QuestionBankItem.options))
        )
        if existing is not None and existing.content_hash == content_hash:
            skipped += 1
            continue

        bank_item = existing or QuestionBankItem(external_id=str(item_payload["id"]))
        if existing is None:
            session.add(bank_item)
        _apply_item_payload(
            bank_item,
            item_payload=item_payload,
            subject=subject,
            concept=concept,
            source_file=path.name,
            source_version=version,
            source_name=source,
            source_hash=source_hash,
            content_hash=content_hash,
        )
        imported += 1

    run.imported_count = imported
    run.skipped_count = skipped
    run.failed_count = len(item_errors)
    run.errors_json = item_errors
    run.completed_at = datetime.now(UTC)
    if item_errors and strict:
        raise ValueError(f"Seed concept validation failed for {path.name}: {item_errors[:3]}")
    return run


def validate_seed_payload(payload: dict[str, Any], *, source_name: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    required = ["version", "source", "language", "subject_code", "education_level", "grade_band", "items"]
    for field in required:
        if field not in payload:
            errors.append({"file": source_name, "error": f"missing_top_level:{field}"})
    if errors:
        return errors
    if not isinstance(payload["items"], list) or not payload["items"]:
        return [{"file": source_name, "error": "items_empty_or_invalid"}]

    seen_ids: set[str] = set()
    for index, item in enumerate(payload["items"], start=1):
        item_id = str(item.get("id", "")).strip()
        item_ref = item_id or f"row:{index}"
        if not item_id:
            errors.append({"file": source_name, "item_id": item_ref, "error": "missing_id"})
        elif item_id in seen_ids:
            errors.append({"file": source_name, "item_id": item_ref, "error": "duplicate_id"})
        seen_ids.add(item_id)

        _validate_item(item, source_name=source_name, item_ref=item_ref, errors=errors)
    return errors


def select_daily_questions(
    session: Session,
    *,
    user: UserAccount,
    limit: int = 3,
) -> tuple[LearnerStep, list[SelectedQuestion]]:
    step = resolve_learner_step(session, user=user)
    candidates = _daily_candidates(session, step=step)
    recent_external_ids = _recent_bank_external_ids(session, user=user)
    selected: list[SelectedQuestion] = []
    now = datetime.now(UTC)

    review_candidates = _ebbinghaus_review_candidates(candidates, step=step, now=now)
    for review_candidate in review_candidates:
        item = _pick_candidate(
            candidates,
            selected=selected,
            concept_id=review_candidate.state.concept_id,
            recent_external_ids=recent_external_ids,
            preferred_language=step.preferred_language,
            education_level=step.education_level,
        )
        if item is not None:
            selected.append(
                SelectedQuestion(
                    item=item,
                    slot=review_candidate.slot,
                    reason=review_candidate.reason,
                    metadata_json=_review_candidate_metadata(review_candidate),
                )
            )
        if len(selected) >= limit:
            return step, selected[:limit]

    fallback_slots = [
        (
            "current_goal_fallback",
            step.active_concept_id,
            "Timestamped review queue is not enough; using the learner's current goal context.",
        ),
        (
            "learning_goal_fallback",
            _learning_goal_fallback_concept_id(session, user=user, step=step),
            "Current goal did not fill the daily set; using the latest learning goal target.",
        ),
    ]
    for slot, concept_id, reason in fallback_slots:
        if concept_id is None:
            continue
        item = _pick_candidate(
            candidates,
            selected=selected,
            concept_id=concept_id,
            recent_external_ids=recent_external_ids,
            preferred_language=step.preferred_language,
            education_level=step.education_level,
        )
        if item is not None:
            selected.append(
                SelectedQuestion(
                    item=item,
                    slot=slot,
                    reason=reason,
                    metadata_json=_fallback_candidate_metadata(
                        slot=slot,
                        timestamp_sufficiency=(
                            "partial" if _has_ebbinghaus_selection(selected) else "insufficient"
                        ),
                    ),
                )
            )
        if len(selected) >= limit:
            return step, selected[:limit]

    while len(selected) < limit:
        item = _pick_candidate(
            candidates,
            selected=selected,
            concept_id=None,
            recent_external_ids=recent_external_ids,
            preferred_language=step.preferred_language,
            education_level=step.education_level,
        )
        if item is None:
            break
        selected.append(
            SelectedQuestion(
                item=item,
                slot="subject_level_fallback",
                reason="No matching timestamped or goal-specific review item; using subject and level fallback.",
                metadata_json=_fallback_candidate_metadata(
                    slot="subject_level_fallback",
                    timestamp_sufficiency=(
                        "partial" if _has_ebbinghaus_selection(selected) else "insufficient"
                    ),
                ),
            )
        )
    return step, selected[:limit]


def resolve_learner_step(session: Session, *, user: UserAccount) -> LearnerStep:
    active_track = _active_track(session, user=user)
    active_module = _active_module(active_track)
    subject = _subject_for_step(session, user=user, active_track=active_track)
    education_level = _education_level_for_user(user)
    preferred_language = _preferred_language_for_user(user)
    active_concept_id = None
    if active_module and active_module.concept_id:
        active_concept_id = active_module.concept_id
    elif active_track and active_track.learning_goal:
        active_concept_id = active_track.learning_goal.target_concept_id

    now = datetime.now(UTC)
    due_states = list(
        session.scalars(
            select(LearnerConceptState)
            .where(
                LearnerConceptState.user_id == user.id,
                or_(
                    LearnerConceptState.status == "review_due",
                    LearnerConceptState.next_review_at <= now,
                ),
            )
            .order_by(
                LearnerConceptState.next_review_at,
                LearnerConceptState.mastery_score,
                LearnerConceptState.confidence_score,
            )
        )
    )
    weak_states = list(
        session.scalars(
            select(LearnerConceptState)
            .where(LearnerConceptState.user_id == user.id)
            .order_by(
                LearnerConceptState.mastery_score,
                LearnerConceptState.confidence_score,
                LearnerConceptState.last_evaluated_at,
            )
        )
    )
    return LearnerStep(
        subject=subject,
        education_level=education_level,
        preferred_language=preferred_language,
        active_track_id=active_track.id if active_track else None,
        active_module_id=active_module.id if active_module else None,
        active_concept_id=active_concept_id,
        due_states=due_states,
        weak_states=weak_states,
    )


def _ebbinghaus_review_candidates(
    candidates: list[QuestionBankItem],
    *,
    step: LearnerStep,
    now: datetime,
) -> list[_EbbinghausCandidate]:
    candidate_concept_ids = {item.concept_id for item in candidates if item.concept_id is not None}
    review_states = [
        state
        for state in {state.concept_id: state for state in [*step.due_states, *step.weak_states]}.values()
        if state.concept_id in candidate_concept_ids and state.last_evaluated_at is not None
    ]
    scored: list[_EbbinghausCandidate] = []
    for state in review_states:
        last_evaluated_at = _as_utc(state.last_evaluated_at)
        next_review_at = _as_utc(state.next_review_at)
        elapsed_days = _elapsed_days(now, last_evaluated_at)
        scheduled_overdue_days = (
            max(0.0, _elapsed_days(now, next_review_at)) if next_review_at else 0.0
        )
        slot = ""
        reason = ""
        if next_review_at and next_review_at <= now:
            slot = "ebbinghaus_due_review"
            reason = "Concept is scheduled for review now based on the learner's spaced repetition state."
        elif elapsed_days >= DAILY_STALE_REVIEW_MIN_DAYS:
            slot = "ebbinghaus_stale_review"
            reason = "Concept was evaluated long enough ago to be at forgetting risk."
        elif (
            (state.mastery_score or 0.0) <= DAILY_LOW_MASTERY_THRESHOLD
            or (state.confidence_score or 0.0) <= DAILY_LOW_MASTERY_THRESHOLD
        ):
            slot = "weak_review_with_timestamp"
            reason = "Concept has a timestamped weak mastery or confidence signal."
        if not slot:
            continue

        estimated_retention = _estimated_retention(state, elapsed_days=elapsed_days)
        forgetting_risk = 1.0 - estimated_retention
        priority_score = (
            scheduled_overdue_days * 100.0
            + forgetting_risk * 50.0
            + (1.0 - _clamp01(state.mastery_score or 0.0)) * 20.0
            + (1.0 - _clamp01(state.confidence_score or 0.0)) * 10.0
        )
        scored.append(
            _EbbinghausCandidate(
                state=state,
                slot=slot,
                reason=reason,
                priority_score=priority_score,
                estimated_retention=estimated_retention,
                forgetting_risk=forgetting_risk,
                elapsed_days=elapsed_days,
                scheduled_overdue_days=scheduled_overdue_days,
            )
        )
    return sorted(
        scored,
        key=lambda item: (
            -item.priority_score,
            _date_sort_value(item.state.next_review_at),
            _date_sort_value(item.state.last_evaluated_at),
            str(item.state.concept_id),
        ),
    )


def _review_candidate_metadata(candidate: _EbbinghausCandidate) -> dict[str, Any]:
    return {
        "selection_strategy": "ebbinghaus_review_queue",
        "timestamp_sufficiency": "sufficient",
        "fallback_path": "none",
        "concept_id": str(candidate.state.concept_id),
        "last_evaluated_at": _iso_or_none(candidate.state.last_evaluated_at),
        "next_review_at": _iso_or_none(candidate.state.next_review_at),
        "elapsed_days": round(candidate.elapsed_days, 4),
        "scheduled_overdue_days": round(candidate.scheduled_overdue_days, 4),
        "estimated_retention": round(candidate.estimated_retention, 4),
        "forgetting_risk": round(candidate.forgetting_risk, 4),
        "priority_score": round(candidate.priority_score, 4),
        "mastery_score": round(float(candidate.state.mastery_score or 0.0), 4),
        "confidence_score": round(float(candidate.state.confidence_score or 0.0), 4),
        "evidence_count": int(candidate.state.evidence_count or 0),
    }


def _fallback_candidate_metadata(
    *,
    slot: str,
    timestamp_sufficiency: str,
) -> dict[str, Any]:
    return {
        "selection_strategy": "fallback_context",
        "timestamp_sufficiency": timestamp_sufficiency,
        "fallback_path": slot.removesuffix("_fallback"),
    }


def _learning_goal_fallback_concept_id(
    session: Session,
    *,
    user: UserAccount,
    step: LearnerStep,
) -> UUID | None:
    track = _active_track(session, user=user)
    concept_id = track.learning_goal.target_concept_id if track and track.learning_goal else None
    if concept_id == step.active_concept_id:
        return None
    return concept_id


def _has_ebbinghaus_selection(selected: list[SelectedQuestion]) -> bool:
    return any(
        choice.slot.startswith("ebbinghaus_")
        or choice.slot == "weak_review_with_timestamp"
        for choice in selected
    )


def _estimated_retention(state: LearnerConceptState, *, elapsed_days: float) -> float:
    retention_strength = 1.0 + float(state.evidence_count or 0) + round(_clamp01(state.mastery_score or 0.0) * 3)
    return _clamp01(math.exp(-(max(0.0, elapsed_days) / max(1.0, retention_strength))))


def _elapsed_days(now: datetime, then: datetime | None) -> float:
    if then is None:
        return 0.0
    return max(0.0, (now - _as_utc(then)).total_seconds() / 86400.0)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _date_sort_value(value: datetime | None) -> str:
    normalized = _as_utc(value)
    return normalized.isoformat() if normalized else "9999-12-31T23:59:59+00:00"


def _iso_or_none(value: datetime | None) -> str | None:
    normalized = _as_utc(value)
    return normalized.isoformat() if normalized else None


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def default_seeds_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "bank_soal" / "seeds"


def _apply_item_payload(
    bank_item: QuestionBankItem,
    *,
    item_payload: dict[str, Any],
    subject: Subject,
    concept: KnowledgeConcept | None,
    source_file: str,
    source_version: str,
    source_name: str,
    source_hash: str,
    content_hash: str,
) -> None:
    bank_item.subject_id = subject.id
    bank_item.concept_id = concept.id if concept else None
    bank_item.subject_code = subject.code
    bank_item.concept_code = str(item_payload["concept_code"]).strip()
    bank_item.concept_title = str(item_payload.get("concept_title") or "")
    bank_item.education_level = str(item_payload["education_level"]).strip()
    bank_item.grade_band = str(item_payload["grade_band"]).strip()
    bank_item.language = str(item_payload["language"]).strip() or "en"
    bank_item.assessment_types_json = [str(item) for item in item_payload["assessment_types"]]
    bank_item.question_type = str(item_payload["question_type"]).strip()
    bank_item.difficulty = str(item_payload["difficulty"]).strip().lower()
    bank_item.cognitive_level = str(item_payload.get("cognitive_level") or "")
    bank_item.prompt = str(item_payload["prompt"]).strip()
    bank_item.helper_text = str(item_payload.get("helper_text") or "")
    bank_item.answer_key = str(item_payload["answer_key"]).strip()
    bank_item.explanation = str(item_payload["explanation"]).strip()
    bank_item.status = str(item_payload["status"]).strip()
    bank_item.rubric_json = item_payload.get("rubric") or {}
    bank_item.tags_json = [str(item) for item in item_payload.get("tags") or []]
    bank_item.source_file = source_file
    bank_item.source_version = source_version
    bank_item.source_hash = source_hash
    bank_item.content_hash = content_hash
    bank_item.metadata_json = {
        **(item_payload.get("metadata") or {}),
        "source_name": source_name,
        "concept_mapped": concept is not None,
    }
    bank_item.options.clear()
    for index, option_payload in enumerate(item_payload["options"], start=1):
        label = str(option_payload["label"]).strip()
        bank_item.options.append(
            QuestionBankOption(
                option_key=label,
                label=label,
                text=str(option_payload["text"]).strip(),
                is_correct=label == bank_item.answer_key,
                sort_order=index,
            )
        )


def _find_concept_for_seed(
    session: Session,
    *,
    subject: Subject,
    concept_code: str,
) -> KnowledgeConcept | None:
    exact = session.scalar(
        select(KnowledgeConcept).where(
            KnowledgeConcept.subject_id == subject.id,
            KnowledgeConcept.code == concept_code,
        )
    )
    if exact is not None:
        return exact
    suffix = f"_{concept_code}"
    candidates = list(
        session.scalars(
            select(KnowledgeConcept)
            .where(KnowledgeConcept.subject_id == subject.id)
            .order_by(KnowledgeConcept.display_order, KnowledgeConcept.code)
        )
    )
    for concept in candidates:
        if concept.code.endswith(suffix):
            return concept
        concept_subtype = str(concept.metadata_json.get("concept_subtype") or "")
        if concept_subtype.endswith(f".{concept_code}"):
            return concept
    return None


def _validate_item(
    item: dict[str, Any],
    *,
    source_name: str,
    item_ref: str,
    errors: list[dict[str, Any]],
) -> None:
    required = [
        "subject_code",
        "concept_code",
        "concept_title",
        "education_level",
        "grade_band",
        "language",
        "assessment_types",
        "question_type",
        "difficulty",
        "prompt",
        "options",
        "answer_key",
        "explanation",
        "status",
    ]
    for field in required:
        if field not in item:
            errors.append({"file": source_name, "item_id": item_ref, "error": f"missing:{field}"})
    if "assessment_types" in item:
        assessment_types = item["assessment_types"]
        if not isinstance(assessment_types, list) or not assessment_types:
            errors.append({"file": source_name, "item_id": item_ref, "error": "assessment_types_empty"})
        else:
            unsupported = [item for item in assessment_types if item not in SUPPORTED_ASSESSMENT_TYPES]
            if unsupported:
                errors.append(
                    {
                        "file": source_name,
                        "item_id": item_ref,
                        "error": f"unsupported_assessment_types:{unsupported}",
                    }
                )
    difficulty = str(item.get("difficulty", "")).lower()
    if difficulty and difficulty not in SUPPORTED_DIFFICULTIES:
        errors.append({"file": source_name, "item_id": item_ref, "error": f"bad_difficulty:{difficulty}"})
    status = str(item.get("status", ""))
    if status and status not in SUPPORTED_STATUSES:
        errors.append({"file": source_name, "item_id": item_ref, "error": f"bad_status:{status}"})
    options = item.get("options")
    if not isinstance(options, list) or len(options) != 4:
        errors.append({"file": source_name, "item_id": item_ref, "error": "options_must_have_4_items"})
        return
    labels = [str(option.get("label", "")).strip() for option in options]
    if len(set(labels)) != len(labels):
        errors.append({"file": source_name, "item_id": item_ref, "error": "duplicate_option_labels"})
    answer_key = str(item.get("answer_key", "")).strip()
    if labels.count(answer_key) != 1:
        errors.append({"file": source_name, "item_id": item_ref, "error": "answer_key_missing_from_options"})
    if item.get("status") == "active" and not str(item.get("explanation", "")).strip():
        errors.append({"file": source_name, "item_id": item_ref, "error": "active_missing_explanation"})


def _daily_candidates(session: Session, *, step: LearnerStep) -> list[QuestionBankItem]:
    items = list(
        session.scalars(
            select(QuestionBankItem)
            .where(
                QuestionBankItem.status == "active",
                QuestionBankItem.subject_id == step.subject.id,
            )
            .options(selectinload(QuestionBankItem.options))
            .order_by(QuestionBankItem.external_id)
        )
    )
    daily_items = [
        item
        for item in items
        if "daily_quiz" in (item.assessment_types_json or [])
        and item.question_type == "multiple_choice"
        and item.options
    ]
    matching_level = [
        item
        for item in daily_items
        if not step.education_level or item.education_level == step.education_level
    ]
    return matching_level or daily_items


def _pick_candidate(
    candidates: list[QuestionBankItem],
    *,
    selected: list[SelectedQuestion],
    concept_id: UUID | None,
    recent_external_ids: set[str],
    preferred_language: str,
    education_level: str,
) -> QuestionBankItem | None:
    selected_ids = {choice.item.id for choice in selected}
    pool = [item for item in candidates if item.id not in selected_ids]
    if concept_id is not None:
        exact = [item for item in pool if item.concept_id == concept_id]
        if not exact:
            return None
        pool = exact
    if not pool:
        return None
    not_recent = [item for item in pool if item.external_id not in recent_external_ids]
    if not_recent:
        pool = not_recent

    def score(item: QuestionBankItem) -> tuple[int, str]:
        value = 0
        if concept_id is not None and item.concept_id == concept_id:
            value += 100
        if preferred_language and item.language == preferred_language:
            value += 20
        elif item.language == "en":
            value += 5
        if education_level and item.education_level == education_level:
            value += 10
        if item.difficulty == "easy":
            value += 1
        return (-value, item.external_id)

    return sorted(pool, key=score)[0]


def _recent_bank_external_ids(session: Session, *, user: UserAccount) -> set[str]:
    rows = session.execute(
        select(AssessmentQuestion.metadata_json)
        .join(AssessmentAttempt, AssessmentAttempt.question_id == AssessmentQuestion.id)
        .join(AssessmentSession, AssessmentSession.id == AssessmentAttempt.session_id)
        .where(AssessmentSession.user_id == user.id)
        .order_by(AssessmentAttempt.submitted_at.desc())
        .limit(30)
    )
    external_ids: set[str] = set()
    for row in rows:
        metadata = row[0] or {}
        external_id = metadata.get("question_bank_external_id")
        if external_id:
            external_ids.add(str(external_id))
    return external_ids


def _active_track(session: Session, *, user: UserAccount) -> LearningTrack | None:
    return session.scalar(
        select(LearningTrack)
        .where(LearningTrack.user_id == user.id, LearningTrack.status != "completed")
        .options(selectinload(LearningTrack.modules), selectinload(LearningTrack.learning_goal))
        .order_by(
            LearningTrack.updated_at.desc(),
            LearningTrack.created_at.desc(),
            LearningTrack.id.desc(),
        )
    )


def _active_module(track: LearningTrack | None) -> TrackModule | None:
    if track is None:
        return None
    modules = sorted(track.modules, key=lambda item: item.sort_order)
    for status in ("active", "ready", "locked"):
        match = next((module for module in modules if module.status == status), None)
        if match is not None:
            return match
    return modules[0] if modules else None


def _subject_for_step(
    session: Session,
    *,
    user: UserAccount,
    active_track: LearningTrack | None,
) -> Subject:
    if active_track and active_track.learning_goal:
        subject = session.get(Subject, active_track.learning_goal.subject_id)
        if subject is not None:
            return subject
    profile = user.learner_profile
    candidates = list(profile.selected_subjects if profile else [])
    candidates.extend(["matematika", "math"])
    for candidate in candidates:
        subject = session.scalar(
            select(Subject).where(Subject.code == canonical_subject_code(candidate))
        )
        if subject is not None:
            return subject
    subject = session.scalar(select(Subject).order_by(Subject.display_order))
    if subject is None:
        raise ValueError("Curriculum seed is empty.")
    return subject


def _education_level_for_user(user: UserAccount) -> str:
    profile = user.learner_profile
    if profile is None:
        return ""
    raw = f"{profile.education_level} {profile.grade_level}".lower()
    if any(token in raw for token in ("sd", "elementary", "primary")):
        return "elementary"
    if any(token in raw for token in ("smp", "junior")):
        return "junior_high"
    if any(token in raw for token in ("sma", "senior", "high")):
        return "senior_high"
    return ""


def _preferred_language_for_user(user: UserAccount) -> str:
    return preferred_language_code(user)


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

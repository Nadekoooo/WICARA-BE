from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.accounts.models import UserAccount
from app.modules.curriculum.models import KnowledgeConcept
from app.modules.learning.models import (
    AssessmentAttempt,
    AssessmentOption,
    AssessmentQuestion,
    AssessmentQuestionPack,
    AssessmentSession,
    LearningGoal,
    LearnerConceptState,
    LearningTrack,
)
from app.modules.posttests.schemas import (
    PosttestAnswerResponse,
    PosttestFinalizeResponse,
    PosttestNodeResultRead,
    PosttestQuestionRead,
    PosttestSessionRead,
)
from app.modules.pretests.generation_service import AdaptivePretestGenerationService


class DuplicateQuestionAttempt(Exception):
    pass


class AdaptivePosttestService:
    def __init__(self, *, generation_service: AdaptivePretestGenerationService | None = None) -> None:
        self.generation_service = generation_service or AdaptivePretestGenerationService()

    def start(
        self,
        session: Session,
        *,
        user: UserAccount,
        learning_goal_id: UUID | None,
        track_id: UUID | None,
    ) -> PosttestSessionRead | None:
        goal = _resolve_goal(session, user=user, learning_goal_id=learning_goal_id, track_id=track_id)
        if goal is None:
            return None

        existing = _active_posttest_for_goal(session, user=user, goal_id=goal.id)
        if existing is not None:
            return self.read(session, user=user, session_id=existing.id)

        diagnosis = (goal.metadata_json or {}).get("diagnosis", {})
        nodes = diagnosis.get("nodes", []) if isinstance(diagnosis, dict) else []
        selected_nodes = [
            node for node in nodes
            if isinstance(node, dict) and str(node.get("status")) in {"gap", "fragile", "partial"}
        ]
        if not selected_nodes:
            raise ValueError("No remediation nodes found from pretest diagnosis.")

        queue: list[dict[str, Any]] = []
        all_question_ids: list[str] = []
        language = _preferred_language(user)

        assessment = AssessmentSession(
            user_id=user.id,
            learning_goal_id=goal.id,
            track_id=goal.track.id if goal.track else None,
            target_concept_id=goal.target_concept_id,
            session_type="posttest",
            title=f"Adaptive posttest: {goal.normalized_topic}",
            status="active",
            source="adaptive_generated",
            metadata_json={"source": "adaptive_generated", "generation": "adaptive_node_posttest_v1"},
            decision_state_json={},
            graph_scope_json={},
            max_questions=max(3, len(selected_nodes) * 3),
            max_depth=0,
            max_nodes_visited=len(selected_nodes),
        )
        session.add(assessment)
        session.flush()

        for node in selected_nodes:
            concept_code = str(node.get("concept_code") or "").strip()
            concept_title = str(node.get("title") or concept_code)
            concept = _concept_by_code(session, concept_code)
            if concept is None:
                continue
            question_ids = self._ensure_three_medium_hard_questions(
                session,
                assessment=assessment,
                concept=concept,
                concept_title=concept_title,
                language=language,
            )
            queue.append(
                {
                    "concept_id": str(concept.id),
                    "concept_code": concept.code,
                    "concept_title": concept.title,
                    "question_ids": question_ids,
                }
            )
            all_question_ids.extend(question_ids)

        if not queue or not all_question_ids:
            raise ValueError("No posttest questions could be generated for remediation nodes.")

        assessment.decision_state_json = {
            "node_queue": queue,
            "question_queue": all_question_ids,
            "current_index": 0,
            "node_results": {
                item["concept_code"]: {
                    "concept_id": item["concept_id"],
                    "concept_title": item["concept_title"],
                    "total_questions": 3,
                    "answered_count": 0,
                    "correct_count": 0,
                    "scaled_score": 0.0,
                    "passed": False,
                    "retake_required": True,
                }
                for item in queue
            },
        }
        session.commit()
        return self.read(session, user=user, session_id=assessment.id)

    def read(self, session: Session, *, user: UserAccount, session_id: UUID) -> PosttestSessionRead | None:
        assessment = _load_assessment(session, user=user, session_id=session_id)
        if assessment is None:
            return None
        state = assessment.decision_state_json or {}
        question_queue = [str(item) for item in state.get("question_queue", [])]
        current_index = int(state.get("current_index", 0))
        current_question = None
        if assessment.status in {"active", "awaiting_answer"} and current_index < len(question_queue):
            current_question = _question_by_id(assessment, question_queue[current_index])
        questions = [
            _question_to_read(
                session,
                _question_by_id(assessment, question_id),
                current=index + 1,
                total=len(question_queue),
            )
            for index, question_id in enumerate(question_queue)
        ]
        return PosttestSessionRead(
            session_id=assessment.id,
            learning_goal_id=assessment.learning_goal_id,
            track_id=assessment.track_id,
            status=assessment.status,
            current_question=_question_to_read(session, current_question, current=current_index + 1, total=len(question_queue)) if current_question else None,
            questions=[item for item in questions if item is not None],
            node_results=_node_results_read(state),
            question_count=current_index,
            total_questions=len(question_queue),
        )

    def submit_answer(
        self,
        session: Session,
        *,
        user: UserAccount,
        session_id: UUID,
        question_id: UUID,
        selected_option_id: UUID,
        confidence: int,
    ) -> PosttestAnswerResponse | None:
        assessment = _load_assessment(session, user=user, session_id=session_id)
        if assessment is None:
            return None
        if assessment.status not in {"active", "awaiting_answer"}:
            raise ValueError("Posttest is not active.")

        question = _question_by_id(assessment, str(question_id))
        if question is None:
            raise LookupError("Question was not found in this posttest session.")
        if session.scalar(select(AssessmentAttempt.id).where(AssessmentAttempt.session_id == assessment.id, AssessmentAttempt.question_id == question.id)):
            raise DuplicateQuestionAttempt()

        option = next((item for item in question.options if item.id == selected_option_id), None)
        if option is None:
            raise LookupError("Selected option was not found for this question.")

        is_correct = bool(option.is_correct)
        attempt = AssessmentAttempt(
            session_id=assessment.id,
            question_id=question.id,
            selected_option_id=option.id,
            confidence=confidence,
            explanation_text="",
            typed_reasoning="",
            used_canvas=False,
            score=1.0 if is_correct else 0.0,
            is_correct=is_correct,
            answer_score=1.0 if is_correct else 0.0,
            reasoning_score=None,
            canvas_score=None,
            evidence_score=1.0 if is_correct else 0.0,
            diagnostic_signal="posttest_correct" if is_correct else "posttest_incorrect",
            evaluated_result={"verdict": "CORRECT" if is_correct else "INCORRECT"},
            evaluation_metadata_json={"source": "posttest_objective", "confidence": confidence},
        )
        session.add(attempt)

        state = assessment.decision_state_json or {}
        node_results = state.get("node_results", {}) if isinstance(state.get("node_results"), dict) else {}
        concept_code = str(question.metadata_json.get("concept_code") or _concept_code(session, question))
        node_state = node_results.get(concept_code)
        if node_state is None:
            raise ValueError("Node state was not found for this posttest question.")

        node_state["answered_count"] = int(node_state.get("answered_count", 0)) + 1
        node_state["correct_count"] = int(node_state.get("correct_count", 0)) + (1 if is_correct else 0)
        total_questions = max(1, int(node_state.get("total_questions", 3)))
        scaled_score = round((int(node_state["correct_count"]) / total_questions) * 10, 1)
        passed = scaled_score >= 7.0 and int(node_state["answered_count"]) >= total_questions
        node_state["scaled_score"] = scaled_score
        node_state["passed"] = passed
        node_state["retake_required"] = not passed

        question_queue = [str(item) for item in state.get("question_queue", [])]
        current_index = int(state.get("current_index", 0)) + 1
        state["current_index"] = current_index
        state["node_results"] = node_results
        assessment.decision_state_json = state

        completed = current_index >= len(question_queue)
        next_question = None
        if completed:
            assessment.status = "completed"
            assessment.completed_at = datetime.now(UTC)
        else:
            next_question = _question_by_id(assessment, question_queue[current_index])

        session.commit()
        return PosttestAnswerResponse(
            attempt_id=attempt.id,
            is_correct=is_correct,
            node_result=_node_result_read(concept_code, node_state),
            next_question=_question_to_read(session, next_question, current=current_index + 1, total=len(question_queue)) if next_question else None,
            completed=completed,
        )

    def finalize(self, session: Session, *, user: UserAccount, session_id: UUID) -> PosttestFinalizeResponse | None:
        assessment = _load_assessment(session, user=user, session_id=session_id)
        if assessment is None:
            return None

        state = assessment.decision_state_json or {}
        node_results = state.get("node_results", {}) if isinstance(state.get("node_results"), dict) else {}
        now_iso = datetime.now(UTC).isoformat()

        for concept_code, payload in node_results.items():
            concept = _concept_by_code(session, concept_code)
            if concept is None:
                continue
            concept_state = session.scalar(select(LearnerConceptState).where(LearnerConceptState.user_id == user.id, LearnerConceptState.concept_id == concept.id))
            if concept_state is None:
                concept_state = LearnerConceptState(
                    user_id=user.id,
                    concept_id=concept.id,
                    status="review_due",
                    mastery_score=0.0,
                    confidence_score=0.0,
                    evidence_count=0,
                )
                session.add(concept_state)
            concept_state.status = "mastered" if payload.get("passed") is True else "review_due"
            concept_state.last_evaluated_at = datetime.now(UTC)

        assessment.status = "completed"
        assessment.completed_at = assessment.completed_at or datetime.now(UTC)
        assessment.metadata_json = {
            **(assessment.metadata_json or {}),
            "posttest_finalized_at": now_iso,
            "node_results": node_results,
        }
        session.commit()

        node_reads = _node_results_read(state)
        return PosttestFinalizeResponse(
            session_id=assessment.id,
            status=assessment.status,
            node_results=node_reads,
            retake_required_concepts=[item.concept_code for item in node_reads if item.retake_required],
        )

    def _ensure_three_medium_hard_questions(
        self,
        session: Session,
        *,
        assessment: AssessmentSession,
        concept: KnowledgeConcept,
        concept_title: str,
        language: str,
    ) -> list[str]:
        pack = self.generation_service.ensure_pack(session, assessment=assessment, concept=concept, language=language)
        selected_ids: list[str] = []
        seen_prompts: set[str] = set()

        for difficulty in ("hard", "medium"):
            question = self.generation_service.question_for_difficulty(pack, difficulty=difficulty)
            key = question.prompt.strip().lower()
            if key not in seen_prompts:
                seen_prompts.add(key)
                selected_ids.append(str(question.id))

        attempts = 0
        while len(selected_ids) < 3 and attempts < 2:
            attempts += 1
            payload_pack, metadata = self.generation_service._generate_pack(concept=concept, language=language)
            for difficulty in ("hard", "medium"):
                payload = payload_pack[difficulty]
                key = str(payload.get("prompt", "")).strip().lower()
                if not key or key in seen_prompts:
                    continue
                question = AssessmentQuestion(
                    session_id=assessment.id,
                    pack_id=pack.id,
                    concept_id=concept.id,
                    step_label="Adaptive Posttest",
                    topic=concept_title,
                    prompt=str(payload["prompt"]),
                    helper_text=str(payload.get("helper_text", "")),
                    difficulty_label=difficulty,
                    sort_order=len(assessment.questions) + 1,
                    metadata_json={
                        "source": "adaptive_generated_posttest",
                        "concept_code": concept.code,
                        "correct_option_key": _correct_label(payload),
                        "explanation": payload.get("explanation", ""),
                    },
                    generation_source=str(metadata.get("generation_source") or "adaptive_generated_posttest"),
                    generation_prompt_version="adaptive_posttest_v1",
                    llm_metadata_json=metadata,
                    expected_reasoning=str(payload.get("expected_reasoning", "")),
                    rubric_json=payload.get("rubric", {}),
                )
                session.add(question)
                session.flush()
                for idx, option in enumerate(payload["options"], start=1):
                    session.add(
                        AssessmentOption(
                            question_id=question.id,
                            option_key=str(option["label"]),
                            label=str(option["label"]),
                            text=str(option["text"]),
                            is_correct=bool(option["is_correct"]),
                            sort_order=idx,
                        )
                    )
                session.flush()
                seen_prompts.add(key)
                selected_ids.append(str(question.id))
                if len(selected_ids) >= 3:
                    break

        if len(selected_ids) < 3:
            raise ValueError(f"Could not generate 3 medium-hard posttest questions for concept {concept.code}.")
        return selected_ids[:3]


def _resolve_goal(
    session: Session,
    *,
    user: UserAccount,
    learning_goal_id: UUID | None,
    track_id: UUID | None,
) -> LearningGoal | None:
    if learning_goal_id is not None:
        return session.scalar(select(LearningGoal).where(LearningGoal.id == learning_goal_id, LearningGoal.user_id == user.id))
    if track_id is not None:
        track = session.scalar(select(LearningTrack).where(LearningTrack.id == track_id, LearningTrack.user_id == user.id))
        if track is None:
            return None
        return session.get(LearningGoal, track.learning_goal_id)
    return None


def _active_posttest_for_goal(session: Session, *, user: UserAccount, goal_id: UUID) -> AssessmentSession | None:
    return session.scalar(
        select(AssessmentSession)
        .where(
            AssessmentSession.user_id == user.id,
            AssessmentSession.learning_goal_id == goal_id,
            AssessmentSession.session_type == "posttest",
            AssessmentSession.status.in_({"active", "awaiting_answer"}),
        )
        .options(selectinload(AssessmentSession.questions).selectinload(AssessmentQuestion.options))
        .order_by(AssessmentSession.created_at.desc())
    )


def _load_assessment(session: Session, *, user: UserAccount, session_id: UUID) -> AssessmentSession | None:
    return session.scalar(
        select(AssessmentSession)
        .where(AssessmentSession.id == session_id, AssessmentSession.user_id == user.id, AssessmentSession.session_type == "posttest")
        .options(selectinload(AssessmentSession.questions).selectinload(AssessmentQuestion.options), selectinload(AssessmentSession.question_packs).selectinload(AssessmentQuestionPack.questions))
    )


def _question_by_id(assessment: AssessmentSession, question_id: str) -> AssessmentQuestion | None:
    return next((question for question in assessment.questions if str(question.id) == question_id), None)


def _question_to_read(session: Session, question: AssessmentQuestion | None, *, current: int, total: int) -> PosttestQuestionRead | None:
    if question is None:
        return None
    concept = session.get(KnowledgeConcept, question.concept_id) if question.concept_id else None
    return PosttestQuestionRead(
        id=question.id,
        concept_id=question.concept_id,
        concept_code=concept.code if concept else str(question.metadata_json.get("concept_code", "")),
        concept_title=concept.title if concept else question.topic,
        difficulty=question.difficulty_label.lower(),
        prompt=question.prompt,
        helper=question.helper_text,
        options=[{"id": option.id, "label": option.label, "text": option.text} for option in question.options],
        progress={"current": current, "max": total},
    )


def _node_result_read(concept_code: str, payload: dict[str, Any]) -> PosttestNodeResultRead:
    concept_id = payload.get("concept_id")
    return PosttestNodeResultRead(
        concept_id=UUID(str(concept_id)) if concept_id else None,
        concept_code=concept_code,
        concept_title=str(payload.get("concept_title") or concept_code),
        total_questions=int(payload.get("total_questions", 3)),
        answered_count=int(payload.get("answered_count", 0)),
        correct_count=int(payload.get("correct_count", 0)),
        scaled_score=float(payload.get("scaled_score", 0.0)),
        passed=bool(payload.get("passed", False)),
        retake_required=bool(payload.get("retake_required", True)),
    )


def _node_results_read(state: dict[str, Any]) -> list[PosttestNodeResultRead]:
    node_results = state.get("node_results", {}) if isinstance(state.get("node_results"), dict) else {}
    return [_node_result_read(code, payload) for code, payload in node_results.items() if isinstance(payload, dict)]


def _concept_by_code(session: Session, concept_code: str) -> KnowledgeConcept | None:
    return session.scalar(select(KnowledgeConcept).where(KnowledgeConcept.code == concept_code))


def _concept_code(session: Session, question: AssessmentQuestion) -> str:
    concept = session.get(KnowledgeConcept, question.concept_id) if question.concept_id else None
    return concept.code if concept else ""


def _correct_label(payload: dict[str, Any]) -> str:
    for option in payload.get("options", []):
        if option.get("is_correct") is True:
            return str(option.get("label") or "")
    return ""


def _preferred_language(user: UserAccount) -> str:
    if user.learner_profile and user.learner_profile.preferred_language:
        return user.learner_profile.preferred_language
    return "id"

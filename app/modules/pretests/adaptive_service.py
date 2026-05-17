from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.accounts.models import UserAccount
from app.modules.curriculum.models import KnowledgeConcept
from app.modules.evidence.models import ImageAsset
from app.modules.learning.models import (
    AssessmentAttempt,
    AssessmentOption,
    AssessmentQuestion,
    AssessmentQuestionPack,
    AssessmentSession,
    LearningGoal,
)
from app.modules.pretests.decision_engine import PretestDecisionEngine
from app.modules.pretests.diagnosis_service import PATH_OPTIONS, PretestDiagnosisService
from app.modules.pretests.evidence_evaluator import PretestEvidenceEvaluator
from app.modules.pretests.generation_service import AdaptivePretestGenerationService
from app.modules.pretests.graph_scope_builder import GraphScopeBuilder
from app.modules.pretests.schemas import (
    PretestAnswerResponse,
    PretestEvaluationRead,
    PretestFinalizeResponse,
    PretestQuestionRead,
    PretestSessionRead,
)


class DuplicateQuestionAttempt(Exception):
    pass


class AdaptivePretestService:
    def __init__(
        self,
        *,
        graph_builder: GraphScopeBuilder | None = None,
        generation_service: AdaptivePretestGenerationService | None = None,
        decision_engine: PretestDecisionEngine | None = None,
        evidence_evaluator: PretestEvidenceEvaluator | None = None,
        diagnosis_service: PretestDiagnosisService | None = None,
    ) -> None:
        self.graph_builder = graph_builder or GraphScopeBuilder()
        self.generation_service = generation_service or AdaptivePretestGenerationService()
        self.decision_engine = decision_engine or PretestDecisionEngine()
        self.evidence_evaluator = evidence_evaluator or PretestEvidenceEvaluator()
        self.diagnosis_service = diagnosis_service or PretestDiagnosisService()

    def start(
        self,
        session: Session,
        *,
        user: UserAccount,
        learning_goal_id: UUID,
        depth: int = 2,
        max_questions: int = 10,
        max_nodes_visited: int = 5,
    ) -> PretestSessionRead | None:
        existing = _active_pretest_for_goal(session, user=user, learning_goal_id=learning_goal_id)
        if existing is not None:
            return self.read(session, user=user, session_id=existing.id)

        goal = session.scalar(
            select(LearningGoal).where(LearningGoal.id == learning_goal_id, LearningGoal.user_id == user.id)
        )
        if goal is None:
            return None
        if goal.status not in {"confirmed", "pretest_in_progress"}:
            raise ValueError("Learning goal is not ready for pretest.")
        if goal.target_concept_id is None:
            raise ValueError("Learning goal has no target concept.")

        target = session.get(KnowledgeConcept, goal.target_concept_id)
        if target is None:
            raise ValueError("Target concept was not found.")
        graph_scope = self.graph_builder.build(
            session,
            target_concept_id=target.id,
            max_depth=depth,
        )
        assessment = AssessmentSession(
            user_id=user.id,
            learning_goal_id=goal.id,
            track_id=goal.track.id if goal.track else None,
            target_concept_id=target.id,
            session_type="pretest",
            title=f"Adaptive pretest: {target.title}",
            status="active",
            source="adaptive_generated",
            graph_scope_json=graph_scope,
            decision_state_json={},
            max_depth=depth,
            max_questions=max_questions,
            max_nodes_visited=max_nodes_visited,
            metadata_json={"source": "adaptive_generated", "generation": "lazy_node_pack"},
        )
        session.add(assessment)
        session.flush()

        pack = self.generation_service.ensure_pack(
            session,
            assessment=assessment,
            concept=target,
            language=_preferred_language(user),
        )
        question = self.generation_service.question_for_difficulty(pack, difficulty="medium")
        decision_state = {
            "target_concept_code": target.code,
            "current_concept_code": target.code,
            "current_difficulty": "medium",
            "current_pack_id": str(pack.id),
            "current_question_id": str(question.id),
            "question_count": 1,
            "max_questions": max_questions,
            "max_depth": depth,
            "max_nodes_visited": max_nodes_visited,
            "max_questions_per_node": 2,
            "confidence_threshold": 0.95,
            "probe_queue": self.graph_builder.build_probe_queue(graph_scope),
            "generated_packs": {
                target.code: self.generation_service.pack_state(pack),
            },
            "node_results": {},
            "confidence": 0.0,
            "stop_reason": None,
        }
        assessment.decision_state_json = decision_state
        goal.status = "pretest_in_progress"
        session.commit()
        return self.read(session, user=user, session_id=assessment.id)

    def read(
        self,
        session: Session,
        *,
        user: UserAccount,
        session_id: UUID,
    ) -> PretestSessionRead | None:
        assessment = _load_assessment(session, user=user, session_id=session_id)
        if assessment is None:
            return None
        state = assessment.decision_state_json or {}
        current_question = None
        question_id = state.get("current_question_id")
        if question_id and assessment.status in {"active", "awaiting_answer"}:
            question = _question_by_id(assessment, str(question_id))
            if question is not None:
                current_question = _question_to_read(session, question, state=state)
        target = session.get(KnowledgeConcept, assessment.target_concept_id) if assessment.target_concept_id else None
        return PretestSessionRead(
            session_id=assessment.id,
            learning_goal_id=assessment.learning_goal_id,
            status=assessment.status,
            target_concept={
                "concept_id": str(target.id) if target else None,
                "concept_code": target.code if target else "",
                "title": target.title if target else "",
            },
            graph_scope=assessment.graph_scope_json or {},
            decision_state=state,
            current_question=current_question,
            question_count=int(state.get("question_count", 0)),
            max_questions=assessment.max_questions,
        )

    def submit_answer(
        self,
        session: Session,
        *,
        user: UserAccount,
        session_id: UUID,
        question_id: UUID,
        selected_option_id: UUID,
        typed_reasoning: str,
        canvas_asset_id: UUID | None,
        used_canvas: bool,
    ) -> PretestAnswerResponse | None:
        assessment = _load_assessment(session, user=user, session_id=session_id)
        if assessment is None:
            return None
        if assessment.status not in {"active", "awaiting_answer"}:
            raise ValueError("Pretest is not active.")
        question = _question_by_id(assessment, str(question_id))
        if question is None:
            raise LookupError("Question was not found in this pretest session.")
        if session.scalar(
            select(AssessmentAttempt.id).where(
                AssessmentAttempt.session_id == assessment.id,
                AssessmentAttempt.question_id == question.id,
            )
        ):
            raise DuplicateQuestionAttempt()
        option = next((item for item in question.options if item.id == selected_option_id), None)
        if option is None:
            raise LookupError("Selected option was not found for this question.")
        if canvas_asset_id is not None:
            asset = session.get(ImageAsset, canvas_asset_id)
            if asset is None or asset.user_id != user.id:
                raise LookupError("Canvas asset was not found.")

        evaluation = self.evidence_evaluator.evaluate(
            session,
            question=question,
            selected_option=option,
            typed_reasoning=typed_reasoning,
            canvas_asset_id=canvas_asset_id,
            used_canvas=used_canvas,
        )
        attempt = AssessmentAttempt(
            session_id=assessment.id,
            question_id=question.id,
            selected_option_id=option.id,
            canvas_asset_id=canvas_asset_id,
            confidence=int(round(float(evaluation["confidence"]) * 10)),
            explanation_text=typed_reasoning.strip(),
            typed_reasoning=typed_reasoning.strip(),
            used_canvas=used_canvas or canvas_asset_id is not None,
            score=float(evaluation["answer_score"]),
            is_correct=bool(evaluation["is_correct"]),
            answer_score=float(evaluation["answer_score"]),
            reasoning_score=evaluation["reasoning_score"],
            canvas_score=evaluation["canvas_score"],
            evidence_score=float(evaluation["evidence_score"]),
            diagnostic_signal=str(evaluation["diagnostic_signal"]),
            evaluated_result={
                "verdict": "CORRECT" if evaluation["is_correct"] else "INCORRECT",
                "diagnostic_signal": evaluation["diagnostic_signal"],
                "reasoning_signal": evaluation["reasoning_signal"],
                "reasoning_feedback": evaluation["reasoning_feedback"],
            },
            evaluation_metadata_json={
                "canvas_status": evaluation["canvas_status"],
                "confidence": evaluation["confidence"],
                "reasoning_signal": evaluation["reasoning_signal"],
                "reasoning_feedback": evaluation["reasoning_feedback"],
                "reasoning_evaluation_source": evaluation["reasoning_evaluation_source"],
            },
        )
        session.add(attempt)

        state = self.decision_engine.record_attempt(
            assessment.decision_state_json or {},
            concept_code=str(question.metadata_json.get("concept_code") or _concept_code(session, question)),
            difficulty=question.difficulty_label.lower(),
            is_correct=bool(evaluation["is_correct"]),
            evidence_score=float(evaluation["evidence_score"]),
            confidence=float(evaluation["confidence"]),
            answer_score=float(evaluation["answer_score"]),
            reasoning_score=evaluation["reasoning_score"],
            canvas_score=evaluation["canvas_score"],
            diagnostic_signal=str(evaluation["diagnostic_signal"]),
            reasoning_signal=str(evaluation["reasoning_signal"]),
        )
        state, next_action = self.decision_engine.decide(
            state,
            last_concept_code=str(question.metadata_json.get("concept_code") or _concept_code(session, question)),
            last_difficulty=question.difficulty_label.lower(),
            last_is_correct=bool(evaluation["is_correct"]),
            graph_scope=assessment.graph_scope_json or {},
        )
        assessment.decision_state_json = state

        if next_action["type"] == "finalize":
            diagnosis = self.diagnosis_service.finalize(
                session,
                user=user,
                assessment=assessment,
                stop_reason=str(next_action["reason"]),
            )
            return PretestAnswerResponse(
                attempt_id=attempt.id,
                evaluation=_evaluation_to_read(evaluation),
                next_action=next_action,
                diagnosis=diagnosis,
            )

        next_question = self._prepare_next_question(
            session,
            user=user,
            assessment=assessment,
            state=state,
            next_action=next_action,
        )
        session.commit()
        return PretestAnswerResponse(
            attempt_id=attempt.id,
            evaluation=_evaluation_to_read(evaluation),
            next_action=next_action,
            next_question=_question_to_read(session, next_question, state=assessment.decision_state_json or {}),
        )

    def finalize(
        self,
        session: Session,
        *,
        user: UserAccount,
        session_id: UUID,
    ) -> PretestFinalizeResponse | None:
        assessment = _load_assessment(session, user=user, session_id=session_id)
        if assessment is None:
            return None
        state = assessment.decision_state_json or {}
        stop_reason = str(state.get("stop_reason") or "manual_finalize")
        diagnosis = self.diagnosis_service.finalize(
            session,
            user=user,
            assessment=assessment,
            stop_reason=stop_reason,
        )
        return PretestFinalizeResponse(
            session_id=assessment.id,
            status="completed",
            diagnosis=diagnosis,
            path_options=PATH_OPTIONS,
        )

    def _prepare_next_question(
        self,
        session: Session,
        *,
        user: UserAccount,
        assessment: AssessmentSession,
        state: dict[str, Any],
        next_action: dict[str, Any],
    ) -> AssessmentQuestion:
        concept_code = str(next_action["concept_code"])
        difficulty = str(next_action["difficulty"])
        concept = _concept_by_code(session, concept_code)
        if concept is None:
            state["stop_reason"] = "concept_not_found"
            assessment.decision_state_json = state
            raise LookupError("Next concept was not found.")
        generated_packs = state.setdefault("generated_packs", {})
        pack_info = generated_packs.get(concept_code)
        pack = None
        if pack_info:
            pack = session.scalar(
                select(AssessmentQuestionPack)
                .where(AssessmentQuestionPack.id == UUID(str(pack_info["pack_id"])))
                .options(
                    selectinload(AssessmentQuestionPack.questions).selectinload(
                        AssessmentQuestion.options
                    )
                )
            )
        if pack is None:
            pack = self.generation_service.ensure_pack(
                session,
                assessment=assessment,
                concept=concept,
                language=_preferred_language(user),
            )
            generated_packs[concept_code] = self.generation_service.pack_state(pack)
        question = self.generation_service.question_for_difficulty(pack, difficulty=difficulty)
        state["current_concept_code"] = concept_code
        state["current_difficulty"] = difficulty
        state["current_pack_id"] = str(pack.id)
        state["current_question_id"] = str(question.id)
        state["question_count"] = int(state.get("question_count", 0)) + 1
        assessment.decision_state_json = state
        return question


def _active_pretest_for_goal(
    session: Session,
    *,
    user: UserAccount,
    learning_goal_id: UUID,
) -> AssessmentSession | None:
    return session.scalar(
        select(AssessmentSession)
        .where(
            AssessmentSession.user_id == user.id,
            AssessmentSession.learning_goal_id == learning_goal_id,
            AssessmentSession.session_type == "pretest",
            AssessmentSession.status.in_({"active", "awaiting_answer"}),
        )
        .options(
            selectinload(AssessmentSession.questions).selectinload(AssessmentQuestion.options),
            selectinload(AssessmentSession.question_packs).selectinload(
                AssessmentQuestionPack.questions
            ),
        )
        .order_by(AssessmentSession.created_at.desc())
    )


def _load_assessment(
    session: Session,
    *,
    user: UserAccount,
    session_id: UUID,
) -> AssessmentSession | None:
    return session.scalar(
        select(AssessmentSession)
        .where(AssessmentSession.id == session_id, AssessmentSession.user_id == user.id)
        .options(
            selectinload(AssessmentSession.questions).selectinload(AssessmentQuestion.options),
            selectinload(AssessmentSession.question_packs).selectinload(
                AssessmentQuestionPack.questions
            ),
        )
    )


def _question_by_id(
    assessment: AssessmentSession,
    question_id: str,
) -> AssessmentQuestion | None:
    return next((question for question in assessment.questions if str(question.id) == question_id), None)


def _question_to_read(
    session: Session,
    question: AssessmentQuestion,
    *,
    state: dict[str, Any],
) -> PretestQuestionRead:
    concept = session.get(KnowledgeConcept, question.concept_id) if question.concept_id else None
    return PretestQuestionRead(
        id=question.id,
        pack_id=question.pack_id,
        concept_code=concept.code if concept else str(question.metadata_json.get("concept_code", "")),
        concept_title=concept.title if concept else question.topic,
        difficulty=question.difficulty_label.lower(),
        prompt=question.prompt,
        helper=question.helper_text,
        options=[
            {"id": option.id, "label": option.label, "text": option.text}
            for option in question.options
        ],
        progress={
            "current": int(state.get("question_count", 0)),
            "max": int(state.get("max_questions", 10)),
        },
    )


def _evaluation_to_read(evaluation: dict[str, Any]) -> PretestEvaluationRead:
    return PretestEvaluationRead(
        is_correct=bool(evaluation["is_correct"]),
        answer_score=float(evaluation["answer_score"]),
        reasoning_score=evaluation["reasoning_score"],
        reasoning_signal=evaluation["reasoning_signal"],
        reasoning_feedback=evaluation["reasoning_feedback"],
        reasoning_evaluation_source=evaluation["reasoning_evaluation_source"],
        canvas_score=evaluation["canvas_score"],
        evidence_score=float(evaluation["evidence_score"]),
        confidence=float(evaluation["confidence"]),
        diagnostic_signal=str(evaluation["diagnostic_signal"]),
        canvas_status=evaluation["canvas_status"],
    )


def _concept_by_code(session: Session, concept_code: str) -> KnowledgeConcept | None:
    return session.scalar(select(KnowledgeConcept).where(KnowledgeConcept.code == concept_code))


def _concept_code(session: Session, question: AssessmentQuestion) -> str:
    concept = session.get(KnowledgeConcept, question.concept_id) if question.concept_id else None
    return concept.code if concept else ""


def _preferred_language(user: UserAccount) -> str:
    if user.learner_profile and user.learner_profile.preferred_language:
        return user.learner_profile.preferred_language
    return "id"

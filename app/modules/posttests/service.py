from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.language import preferred_language_code
from app.modules.accounts.models import UserAccount
from app.modules.assessments.metrics import AssessmentEvidenceEvaluator, PASS_PERCENT
from app.modules.curriculum.models import KnowledgeConcept
from app.modules.evidence.models import ImageAsset
from app.modules.learning.models import (
    AssessmentAttempt,
    AssessmentQuestion,
    AssessmentQuestionPack,
    AssessmentSession,
    LearningGoal,
    LearnerConceptState,
    LearningTrack,
    TrackModule,
)
from app.modules.posttests.schemas import (
    PosttestAnswerResponse,
    PosttestEvaluationRead,
    PosttestFinalizeResponse,
    PosttestNodeResultRead,
    PosttestQuestionRead,
    PosttestSessionRead,
)
from app.modules.pretests.generation_service import AdaptivePretestGenerationService


class DuplicateQuestionAttempt(Exception):
    pass


REMEDIATION_NODE_STATUSES = {"gap", "fragile", "partial"}
POSTTEST_PASS_SCORE = PASS_PERCENT
POSTTEST_TARGET_DIFFICULTIES = ("medium", "medium", "medium", "hard", "hard")
POSTTEST_PREREQUISITE_DIFFICULTIES = ("medium", "hard")


class AdaptivePosttestService:
    def __init__(
        self,
        *,
        generation_service: AdaptivePretestGenerationService | None = None,
        evidence_evaluator: AssessmentEvidenceEvaluator | None = None,
    ) -> None:
        self.generation_service = generation_service or AdaptivePretestGenerationService()
        self.evidence_evaluator = evidence_evaluator or AssessmentEvidenceEvaluator()

    def start(
        self,
        session: Session,
        *,
        user: UserAccount,
        learning_goal_id: UUID | None,
        track_id: UUID | None,
        module_id: UUID | None = None,
    ) -> PosttestSessionRead | None:
        goal, focus_concept_code = _resolve_goal_context(
            session,
            user=user,
            learning_goal_id=learning_goal_id,
            track_id=track_id,
            module_id=module_id,
        )
        if goal is None:
            return None

        existing = _active_posttest_for_goal(session, user=user, goal_id=goal.id)
        if existing is not None:
            return self.read(session, user=user, session_id=existing.id)

        diagnosis = (goal.metadata_json or {}).get("diagnosis", {})
        nodes = diagnosis.get("nodes", []) if isinstance(diagnosis, dict) else []
        remediation_nodes = _remediation_nodes(nodes)
        selected_nodes = _select_posttest_nodes(
            session,
            goal=goal,
            remediation_nodes=remediation_nodes,
            focus_concept_code=focus_concept_code,
        )
        if not selected_nodes:
            raise ValueError("No remediation nodes found from pretest diagnosis.")

        queue: list[dict[str, Any]] = []
        all_question_ids: list[str] = []
        language = _preferred_language(user)
        total_question_count = sum(len(_posttest_difficulties_for_node(node)) for node in selected_nodes)

        assessment = AssessmentSession(
            user_id=user.id,
            learning_goal_id=goal.id,
            track_id=goal.track.id if goal.track else None,
            target_concept_id=goal.target_concept_id,
            session_type="posttest",
            title=f"Adaptive posttest: {goal.normalized_topic}",
            status="active",
            source="adaptive_generated",
            metadata_json={
                "source": "adaptive_generated",
                "generation": "fresh_ai_posttest_v2",
                "question_reuse": "disabled",
                "question_limit": None,
                "target_question_count": len(POSTTEST_TARGET_DIFFICULTIES),
                "prerequisite_question_count": len(POSTTEST_PREREQUISITE_DIFFICULTIES),
                "difficulty_policy": {
                    "target": list(POSTTEST_TARGET_DIFFICULTIES),
                    "prerequisite": list(POSTTEST_PREREQUISITE_DIFFICULTIES),
                },
                "available_node_count": len(remediation_nodes),
                "selected_node_count": len(selected_nodes),
                "omitted_node_count": max(0, len(remediation_nodes) - len(selected_nodes)),
                "focus_concept_code": focus_concept_code,
                "learner_language": language,
            },
            decision_state_json={},
            graph_scope_json={},
            max_questions=total_question_count,
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
            question_ids = self._generate_posttest_questions(
                session,
                assessment=assessment,
                concept=concept,
                concept_title=concept_title,
                node=node,
                language=language,
                diagnosis_context=_node_diagnosis_context(node),
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
                    "total_questions": len(item["question_ids"]),
                    "answered_count": 0,
                    "correct_count": 0,
                    "answer_score_sum": 0.0,
                    "evidence_score_sum": 0.0,
                    "confidence_sum": 0.0,
                    "answer_percent": 0.0,
                    "evidence_percent": 0.0,
                    "score_percent": 0.0,
                    "confidence_percent": 0.0,
                    "scaled_score": 0.0,
                    "passed": False,
                    "retake_required": True,
                    "metric_source": "adaptive_posttest_evidence",
                    "attempts": [],
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
        state = deepcopy(assessment.decision_state_json or {})
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
        typed_reasoning: str = "",
        canvas_asset_id: UUID | None = None,
        used_canvas: bool = False,
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
        is_correct = bool(evaluation["is_correct"])
        attempt = AssessmentAttempt(
            session_id=assessment.id,
            question_id=question.id,
            selected_option_id=option.id,
            canvas_asset_id=canvas_asset_id,
            confidence=confidence,
            explanation_text=typed_reasoning.strip(),
            typed_reasoning=typed_reasoning.strip(),
            used_canvas=used_canvas or canvas_asset_id is not None,
            score=float(evaluation["answer_score"]),
            is_correct=is_correct,
            answer_score=float(evaluation["answer_score"]),
            reasoning_score=evaluation["reasoning_score"],
            canvas_score=evaluation["canvas_score"],
            evidence_score=float(evaluation["evidence_score"]),
            diagnostic_signal=str(evaluation["diagnostic_signal"]),
            evaluated_result={
                "verdict": "CORRECT" if is_correct else "INCORRECT",
                "diagnostic_signal": evaluation["diagnostic_signal"],
                "reasoning_signal": evaluation["reasoning_signal"],
                "reasoning_feedback": evaluation["reasoning_feedback"],
            },
            evaluation_metadata_json={
                "source": "posttest_evidence",
                "self_reported_confidence": confidence,
                "confidence": evaluation["confidence"],
                "canvas_status": evaluation["canvas_status"],
                "reasoning_signal": evaluation["reasoning_signal"],
                "reasoning_feedback": evaluation["reasoning_feedback"],
                "reasoning_evaluation_source": evaluation["reasoning_evaluation_source"],
            },
        )
        session.add(attempt)

        state = deepcopy(assessment.decision_state_json or {})
        node_results = state.get("node_results", {}) if isinstance(state.get("node_results"), dict) else {}
        concept_code = str(question.metadata_json.get("concept_code") or _concept_code(session, question))
        node_state = node_results.get(concept_code)
        if node_state is None:
            raise ValueError("Node state was not found for this posttest question.")

        node_state["answered_count"] = int(node_state.get("answered_count", 0)) + 1
        node_state["correct_count"] = int(node_state.get("correct_count", 0)) + (1 if is_correct else 0)
        node_state["answer_score_sum"] = round(
            float(node_state.get("answer_score_sum") or 0.0) + float(evaluation["answer_score"]),
            4,
        )
        node_state["evidence_score_sum"] = round(
            float(node_state.get("evidence_score_sum") or 0.0) + float(evaluation["evidence_score"]),
            4,
        )
        node_state["confidence_sum"] = round(
            float(node_state.get("confidence_sum") or 0.0) + float(evaluation["confidence"]),
            4,
        )
        attempts = node_state.setdefault("attempts", [])
        if isinstance(attempts, list):
            attempts.append(
                {
                    "question_id": str(question.id),
                    "is_correct": is_correct,
                    "answer_score": round(float(evaluation["answer_score"]), 4),
                    "reasoning_score": (
                        round(float(evaluation["reasoning_score"]), 4)
                        if evaluation["reasoning_score"] is not None
                        else None
                    ),
                    "canvas_score": (
                        round(float(evaluation["canvas_score"]), 4)
                        if evaluation["canvas_score"] is not None
                        else None
                    ),
                    "evidence_score": round(float(evaluation["evidence_score"]), 4),
                    "confidence": round(float(evaluation["confidence"]), 4),
                    "diagnostic_signal": str(evaluation["diagnostic_signal"]),
                    "reasoning_signal": str(evaluation["reasoning_signal"]),
                    "canvas_status": evaluation["canvas_status"],
                }
            )
        _refresh_node_result_score(node_state)

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
            evaluation=_evaluation_to_read(evaluation),
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
        already_finalized = bool((assessment.metadata_json or {}).get("posttest_finalized_at"))

        for concept_code, payload in node_results.items():
            if not isinstance(payload, dict):
                continue
            _refresh_node_result_score(payload)
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
            scaled_mastery = _clamp01(float(payload.get("scaled_score") or 0.0) / 10.0)
            concept_state.status = "mastered" if payload.get("passed") is True else "review_due"
            concept_state.mastery_score = scaled_mastery
            concept_state.confidence_score = scaled_mastery
            if not already_finalized:
                concept_state.evidence_count = (
                    concept_state.evidence_count or 0
                ) + int(payload.get("answered_count") or 0)
            concept_state.last_evaluated_at = datetime.now(UTC)
            concept_state.next_review_at = datetime.now(UTC) + (
                timedelta(days=7) if payload.get("passed") is True else timedelta(days=1)
            )

        assessment.status = "completed"
        assessment.completed_at = assessment.completed_at or datetime.now(UTC)
        assessment.decision_state_json = {**state, "node_results": node_results}
        assessment.metadata_json = {
            **(assessment.metadata_json or {}),
            "posttest_finalized_at": now_iso,
            "node_results": node_results,
        }

        if assessment.learning_goal_id is not None:
            goal = session.get(LearningGoal, assessment.learning_goal_id)
            if goal is not None and goal.status == "in_progress":
                all_passed = bool(node_results) and all(
                    bool(payload.get("passed"))
                    for payload in node_results.values()
                    if isinstance(payload, dict)
                )
                if all_passed:
                    goal.status = "completed"
                    goal.completed_at = datetime.now(UTC)

        session.commit()

        node_reads = _node_results_read(state)
        return PosttestFinalizeResponse(
            session_id=assessment.id,
            status=assessment.status,
            node_results=node_reads,
            retake_required_concepts=[item.concept_code for item in node_reads if item.retake_required],
        )

    def _generate_posttest_questions(
        self,
        session: Session,
        *,
        assessment: AssessmentSession,
        concept: KnowledgeConcept,
        concept_title: str,
        node: dict[str, Any],
        language: str,
        diagnosis_context: str,
    ) -> list[str]:
        node_role = str(node.get("posttest_role") or node.get("role") or "prerequisite")
        questions = self.generation_service.create_fresh_questions(
            session,
            assessment=assessment,
            concept=concept,
            difficulties=list(_posttest_difficulties_for_node(node)),
            assessment_type="posttest",
            language=language,
            node_role="goal" if node_role == "target" else "prerequisite",
            diagnosis_context=diagnosis_context,
            step_label="Adaptive Posttest",
            topic=concept_title,
        )
        return [str(question.id) for question in questions]


def _resolve_goal_context(
    session: Session,
    *,
    user: UserAccount,
    learning_goal_id: UUID | None,
    track_id: UUID | None,
    module_id: UUID | None,
) -> tuple[LearningGoal | None, str | None]:
    focus_concept_code: str | None = None
    resolved_track_id = track_id
    if module_id is not None:
        module = session.scalar(
            select(TrackModule)
            .join(LearningTrack, TrackModule.track_id == LearningTrack.id)
            .where(
                TrackModule.id == module_id,
                LearningTrack.user_id == user.id,
            )
        )
        if module is None:
            return None, None
        resolved_track_id = module.track_id
        if module.concept_id is not None:
            concept = session.get(KnowledgeConcept, module.concept_id)
            if concept is not None:
                focus_concept_code = concept.code

    if learning_goal_id is not None:
        goal = session.scalar(
            select(LearningGoal).where(
                LearningGoal.id == learning_goal_id,
                LearningGoal.user_id == user.id,
            )
        )
        if goal is None:
            return None, focus_concept_code
        if resolved_track_id is not None:
            owned_track_for_goal = session.scalar(
                select(LearningTrack).where(
                    LearningTrack.id == resolved_track_id,
                    LearningTrack.user_id == user.id,
                    LearningTrack.learning_goal_id == goal.id,
                )
            )
            if owned_track_for_goal is None:
                raise ValueError("module_id does not belong to the selected learning_goal_id.")
        return goal, focus_concept_code

    if resolved_track_id is not None:
        track = session.scalar(
            select(LearningTrack).where(
                LearningTrack.id == resolved_track_id,
                LearningTrack.user_id == user.id,
            )
        )
        if track is None:
            return None, focus_concept_code
        goal = session.get(LearningGoal, track.learning_goal_id)
        return goal, focus_concept_code

    return None, focus_concept_code


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
        answer_percent=float(payload.get("answer_percent", 0.0)),
        evidence_percent=float(payload.get("evidence_percent", 0.0)),
        score_percent=float(payload.get("score_percent", 0.0)),
        confidence_percent=float(payload.get("confidence_percent", 0.0)),
        scaled_score=float(payload.get("scaled_score", 0.0)),
        passed=bool(payload.get("passed", False)),
        retake_required=bool(payload.get("retake_required", True)),
        metric_source=str(payload.get("metric_source") or "adaptive_posttest_evidence"),
    )


def _node_results_read(state: dict[str, Any]) -> list[PosttestNodeResultRead]:
    node_results = state.get("node_results", {}) if isinstance(state.get("node_results"), dict) else {}
    return [_node_result_read(code, payload) for code, payload in node_results.items() if isinstance(payload, dict)]


def _evaluation_to_read(evaluation: dict[str, Any]) -> PosttestEvaluationRead:
    return PosttestEvaluationRead(
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


def _remediation_nodes(nodes: object) -> list[dict[str, Any]]:
    if not isinstance(nodes, list):
        return []
    selected = [
        node
        for node in nodes
        if isinstance(node, dict)
        and str(node.get("status")) in REMEDIATION_NODE_STATUSES
    ]
    return sorted(selected, key=_posttest_node_priority)


def _select_posttest_nodes(
    session: Session,
    *,
    goal: LearningGoal,
    remediation_nodes: list[dict[str, Any]],
    focus_concept_code: str | None,
) -> list[dict[str, Any]]:
    primary = _primary_posttest_node(
        session,
        goal=goal,
        remediation_nodes=remediation_nodes,
        focus_concept_code=focus_concept_code,
    )
    selected: list[dict[str, Any]] = []
    if primary is not None:
        selected.append({**primary, "posttest_role": "target"})
    primary_code = str(primary.get("concept_code") or "") if primary else ""
    for node in remediation_nodes:
        concept_code = str(node.get("concept_code") or "").strip()
        if not concept_code or concept_code == primary_code:
            continue
        selected.append({**node, "posttest_role": "prerequisite"})
    return selected


def _primary_posttest_node(
    session: Session,
    *,
    goal: LearningGoal,
    remediation_nodes: list[dict[str, Any]],
    focus_concept_code: str | None,
) -> dict[str, Any] | None:
    if focus_concept_code:
        focused = next(
            (
                node
                for node in remediation_nodes
                if str(node.get("concept_code") or "").strip() == focus_concept_code
            ),
            None,
        )
        if focused is not None:
            return focused
        focused_concept = _concept_by_code(session, focus_concept_code)
        if focused_concept is not None:
            return {
                "concept_id": str(focused_concept.id),
                "concept_code": focused_concept.code,
                "title": focused_concept.title,
                "role": "target",
                "status": "fragile",
                "depth": 0,
            }
    target_node = next(
        (node for node in remediation_nodes if str(node.get("role")) == "target"),
        None,
    )
    if target_node is not None:
        return target_node
    if goal.target_concept_id is None:
        return remediation_nodes[0] if remediation_nodes else None
    target_concept = session.get(KnowledgeConcept, goal.target_concept_id)
    if target_concept is None:
        return remediation_nodes[0] if remediation_nodes else None
    return {
        "concept_id": str(target_concept.id),
        "concept_code": target_concept.code,
        "title": target_concept.title,
        "role": "target",
        "status": "fragile",
        "depth": 0,
    }


def _posttest_difficulties_for_node(node: dict[str, Any]) -> tuple[str, ...]:
    return (
        POSTTEST_TARGET_DIFFICULTIES
        if str(node.get("posttest_role") or node.get("role")) == "target"
        else POSTTEST_PREREQUISITE_DIFFICULTIES
    )


def _node_diagnosis_context(node: dict[str, Any]) -> str:
    return (
        f"concept_code={node.get('concept_code') or ''}; "
        f"title={node.get('title') or ''}; "
        f"role={node.get('role') or ''}; "
        f"status={node.get('status') or ''}; "
        f"depth={node.get('depth') or 0}; "
        f"answer_percent={node.get('answer_percent') or ''}; "
        f"evidence_percent={node.get('evidence_percent') or ''}; "
        f"confidence_percent={node.get('confidence_percent') or ''}"
    )


def _posttest_node_priority(node: dict[str, Any]) -> tuple[int, int, int, str]:
    role_priority = 0 if str(node.get("role")) == "target" else 1
    status_priority = {
        "gap": 0,
        "fragile": 1,
        "partial": 2,
    }.get(str(node.get("status")), 99)
    try:
        depth_priority = -int(node.get("depth") or 0)
    except (TypeError, ValueError):
        depth_priority = 0
    return role_priority, status_priority, depth_priority, str(node.get("concept_code") or "")


def _refresh_node_result_score(payload: dict[str, Any]) -> None:
    total_questions = max(1, int(payload.get("total_questions") or 3))
    answered_count = max(0, int(payload.get("answered_count") or 0))
    correct_count = max(0, int(payload.get("correct_count") or 0))
    answered_for_average = max(1, answered_count)
    answer_score_sum = _float_value(payload.get("answer_score_sum"), fallback=float(correct_count))
    evidence_score_sum = _float_value(payload.get("evidence_score_sum"), fallback=answer_score_sum)
    confidence_sum = _float_value(payload.get("confidence_sum"), fallback=0.0)
    answer_percent = round((answer_score_sum / answered_for_average) * 100, 2)
    evidence_percent = round((evidence_score_sum / answered_for_average) * 100, 2)
    score_percent = evidence_percent
    confidence_percent = round((confidence_sum / answered_for_average) * 100, 2) if answered_count else 0.0
    scaled_score = _posttest_scaled_score(score_percent=score_percent)
    passed = (
        answered_count >= total_questions
        and answer_percent >= POSTTEST_PASS_SCORE
        and score_percent >= POSTTEST_PASS_SCORE
    )
    payload["total_questions"] = total_questions
    payload["answered_count"] = answered_count
    payload["correct_count"] = correct_count
    payload["answer_score_sum"] = round(answer_score_sum, 4)
    payload["evidence_score_sum"] = round(evidence_score_sum, 4)
    payload["confidence_sum"] = round(confidence_sum, 4)
    payload["answer_percent"] = answer_percent
    payload["evidence_percent"] = evidence_percent
    payload["score_percent"] = score_percent
    payload["confidence_percent"] = confidence_percent
    payload["scaled_score"] = scaled_score
    payload["passed"] = passed
    payload["retake_required"] = not passed
    payload["metric_source"] = str(payload.get("metric_source") or "adaptive_posttest_evidence")


def _posttest_scaled_score(*, score_percent: float) -> float:
    return float(round(max(0.0, min(100.0, score_percent)) / 10, 2))


def _float_value(value: object, *, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _concept_by_code(session: Session, concept_code: str) -> KnowledgeConcept | None:
    return session.scalar(select(KnowledgeConcept).where(KnowledgeConcept.code == concept_code))


def _concept_code(session: Session, question: AssessmentQuestion) -> str:
    concept = session.get(KnowledgeConcept, question.concept_id) if question.concept_id else None
    return concept.code if concept else ""


def _preferred_language(user: UserAccount) -> str:
    return preferred_language_code(user)

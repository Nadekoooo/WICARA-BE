from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.accounts.models import UserAccount
from app.modules.learning.models import LearnerConceptState, TrackModule
from app.modules.workspaces.schemas import WorkspaceMasteryUpdateRead


@dataclass(frozen=True)
class WorkspaceMasteryResult:
    update: WorkspaceMasteryUpdateRead | None
    concept_id: UUID | None


class WorkspaceMasteryService:
    def apply_event(
        self,
        session: Session,
        *,
        user: UserAccount,
        module: TrackModule | None,
        event_type: str,
        text_payload: str,
        metadata: dict[str, Any],
    ) -> WorkspaceMasteryResult:
        concept_id = module.concept_id if module else None
        if concept_id is None:
            return WorkspaceMasteryResult(
                update=WorkspaceMasteryUpdateRead(
                    concept_id=None,
                    reason="module_has_no_concept",
                ),
                concept_id=None,
            )

        if event_type == "media_generated":
            return WorkspaceMasteryResult(
                update=WorkspaceMasteryUpdateRead(
                    concept_id=concept_id,
                    reason="media_intervention_recorded_without_mastery_delta",
                ),
                concept_id=concept_id,
            )

        evidence_delta = 0
        mastery_delta = 0.0
        confidence_delta = 0.0
        reason = "no_mastery_signal"

        if event_type == "quiz_answer":
            evidence_delta = 1
            is_correct = _metadata_bool(metadata, "is_correct")
            mastery_delta = 0.08 if is_correct else -0.05
            confidence_delta = 0.06 if is_correct else -0.04
            reason = "quiz_answer_correct" if is_correct else "quiz_answer_needs_review"
        elif event_type == "canvas_sent":
            evidence_delta = 1
            confidence_delta = 0.03
            reason = "canvas_evidence_recorded"
        elif event_type == "text" and _is_meaningful_text(text_payload):
            evidence_delta = 1
            confidence_delta = 0.02
            reason = "text_evidence_recorded"

        if evidence_delta == 0 and mastery_delta == 0 and confidence_delta == 0:
            return WorkspaceMasteryResult(
                update=WorkspaceMasteryUpdateRead(
                    concept_id=concept_id,
                    reason=reason,
                ),
                concept_id=concept_id,
            )

        state = _get_or_create_state(session, user=user, concept_id=concept_id)
        state.mastery_score = _clamp01((state.mastery_score or 0.0) + mastery_delta)
        state.confidence_score = _clamp01(
            (state.confidence_score or 0.0) + confidence_delta
        )
        state.evidence_count = (state.evidence_count or 0) + evidence_delta
        state.last_evaluated_at = datetime.now(UTC)
        if event_type == "quiz_answer" and mastery_delta < 0:
            state.status = "review_due"
            state.next_review_at = datetime.now(UTC) + timedelta(days=1)
        elif state.mastery_score >= 0.7:
            state.status = "mastered"
            state.next_review_at = datetime.now(UTC) + timedelta(days=7)
        else:
            state.status = "ready"
            state.next_review_at = datetime.now(UTC) + timedelta(days=3)

        return WorkspaceMasteryResult(
            update=WorkspaceMasteryUpdateRead(
                concept_id=concept_id,
                mastery_score=state.mastery_score,
                confidence_score=state.confidence_score,
                evidence_count=state.evidence_count,
                status=state.status,
                delta=mastery_delta,
                reason=reason,
            ),
            concept_id=concept_id,
        )


def _get_or_create_state(
    session: Session,
    *,
    user: UserAccount,
    concept_id: UUID,
) -> LearnerConceptState:
    state = session.scalar(
        select(LearnerConceptState).where(
            LearnerConceptState.user_id == user.id,
            LearnerConceptState.concept_id == concept_id,
        )
    )
    if state is not None:
        return state

    state = LearnerConceptState(
        user_id=user.id,
        concept_id=concept_id,
        status="ready",
        mastery_score=0.0,
        confidence_score=0.0,
        evidence_count=0,
    )
    session.add(state)
    return state


def _metadata_bool(metadata: dict[str, Any], key: str) -> bool:
    value = metadata.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "correct"}
    return False


def _is_meaningful_text(text: str) -> bool:
    return len(text.strip().split()) >= 3


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))

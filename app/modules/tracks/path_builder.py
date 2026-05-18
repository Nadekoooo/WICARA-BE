from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.accounts.models import UserAccount
from app.modules.curriculum.models import KnowledgeConcept
from app.modules.learning.models import LearningGoal, LearningTrack, TrackModule
from app.modules.learning_goal_resolution.schemas import PathModuleRead, PathSelectionResponse


PATH_OPTIONS = {
    "review_only",
    "target_reinforcement",
    "target_from_basics",
    "target_intro",
    "repair_prerequisites",
    "full_foundation_path",
}


class TrackBuilderService:
    def select_path(
        self,
        session: Session,
        *,
        user: UserAccount,
        learning_goal_id: UUID,
        path_option: str,
    ) -> PathSelectionResponse | None:
        if path_option not in PATH_OPTIONS:
            raise ValueError("Unsupported path option.")

        goal = session.scalar(
            select(LearningGoal)
            .where(LearningGoal.id == learning_goal_id, LearningGoal.user_id == user.id)
            .options(selectinload(LearningGoal.track).selectinload(LearningTrack.modules))
        )
        if goal is None:
            return None
        if goal.status in {"archived", "cancelled"}:
            raise ValueError("Path selection requires an active learning goal.")

        concepts = _concepts_for_path(session, goal=goal, path_option=path_option)
        track = goal.track
        if track is None:
            title = f"{goal.normalized_topic} path"
            track = LearningTrack(
                user_id=user.id,
                learning_goal_id=goal.id,
                title=title,
                subtitle="Learning path from selected goal",
                status="active",
                progress_percent=0,
                metadata_json={"source": "goal_path_selection", "path_option": path_option},
            )
            session.add(track)
            session.flush()
        else:
            track.status = "active"
            track.metadata_json = {
                **(track.metadata_json or {}),
                "source": "goal_path_selection",
                "path_option": path_option,
            }
            for module in list(track.modules):
                session.delete(module)
            session.flush()

        modules = _module_payloads(goal=goal, concepts=concepts, path_option=path_option)
        for index, payload in enumerate(modules, start=1):
            session.add(
                TrackModule(
                    track_id=track.id,
                    concept_id=payload["concept"].id if payload.get("concept") else None,
                    title=payload["title"],
                    description=payload["description"],
                    estimated_minutes=payload["minutes"],
                    difficulty_label=payload["difficulty"],
                    sort_order=index,
                    status="ready" if index == 1 else "locked",
                    metadata_json={"path_option": path_option},
                )
            )
        goal.status = "in_progress"
        session.commit()

        refreshed = session.scalar(
            select(LearningTrack)
            .where(LearningTrack.id == track.id)
            .options(selectinload(LearningTrack.modules))
        )
        assert refreshed is not None
        concept_by_id = {
            concept.id: concept
            for concept in session.scalars(
                select(KnowledgeConcept).where(
                    KnowledgeConcept.id.in_(
                        [module.concept_id for module in refreshed.modules if module.concept_id]
                    )
                )
            )
        }
        return PathSelectionResponse(
            track_id=refreshed.id,
            goal_status=goal.status,
            modules=[
                PathModuleRead(
                    id=module.id,
                    title=module.title,
                    description=module.description,
                    concept_code=concept_by_id[module.concept_id].code
                    if module.concept_id in concept_by_id
                    else None,
                    difficulty_label=module.difficulty_label,
                    sort_order=module.sort_order,
                    status=module.status,
                )
                for module in refreshed.modules
            ],
            metadata={"path_option": path_option},
        )


def _concepts_for_path(
    session: Session,
    *,
    goal: LearningGoal,
    path_option: str,
) -> list[KnowledgeConcept]:
    target = session.get(KnowledgeConcept, goal.target_concept_id) if goal.target_concept_id else None
    concept_codes: list[str] = []

    if target:
        concept_codes.append(target.code)

    seen: set[str] = set()
    ordered_codes = [code for code in concept_codes if code and not (code in seen or seen.add(code))]
    if not ordered_codes and target:
        ordered_codes = [target.code]
    if not ordered_codes:
        return []

    concepts = {
        concept.code: concept
        for concept in session.scalars(select(KnowledgeConcept).where(KnowledgeConcept.code.in_(ordered_codes)))
    }
    return [concepts[code] for code in ordered_codes if code in concepts]


def _module_payloads(
    *,
    goal: LearningGoal,
    concepts: list[KnowledgeConcept],
    path_option: str,
) -> list[dict[str, object]]:
    if not concepts:
        return [
            {
                "concept": None,
                "title": goal.normalized_topic,
                "description": "Continue from the selected learning goal.",
                "minutes": 12,
                "difficulty": "Medium",
            }
        ]

    modules: list[dict[str, object]] = []
    for index, concept in enumerate(concepts, start=1):
        if path_option == "review_only":
            title = f"Review: {concept.title}"
            description = "Short review and challenge practice for the confirmed learning goal."
            difficulty = "Hard"
        elif index == len(concepts):
            title = concept.title
            description = "Learn the target concept with guided examples and checks."
            difficulty = "Medium"
        else:
            title = f"Repair: {concept.title}"
            description = "Strengthen this prerequisite before returning to the target concept."
            difficulty = "Easy"
        modules.append(
            {
                "concept": concept,
                "title": title,
                "description": description,
                "minutes": 10 if difficulty == "Easy" else 14,
                "difficulty": difficulty,
            }
        )
    return modules

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.accounts.models import UserAccount
from app.modules.curriculum.models import KnowledgeConcept
from app.modules.learning.models import (
    AssessmentSession,
    LearnerConceptState,
    LearningGoal,
    LearningTrack,
    TrackModule,
)
from app.modules.tracks.path_builder import PATH_OPTIONS as TRACK_PATH_OPTIONS
from app.modules.tracks.path_builder import TrackBuilderService
from app.modules.workspaces.models import WorkspaceSession

PATH_OPTIONS = [
    "review_only",
    "target_reinforcement",
    "target_from_basics",
    "target_intro",
    "repair_prerequisites",
    "full_foundation_path",
]


class PretestDiagnosisService:
    def finalize(
        self,
        session: Session,
        *,
        user: UserAccount,
        assessment: AssessmentSession,
        stop_reason: str,
    ) -> dict[str, Any]:
        graph_scope = assessment.graph_scope_json or {}
        state = assessment.decision_state_json or {}
        nodes = _diagnosis_nodes(graph_scope=graph_scope, state=state)
        target = next((node for node in nodes if node["role"] == "target"), None)
        recommended_path = _recommended_path(nodes=nodes, stop_reason=stop_reason)
        analysis = _analysis_report(
            nodes=nodes,
            target=target,
            recommended_path=recommended_path,
            stop_reason=stop_reason,
        )
        diagnosis = {
            "summary": _summary(target=target, recommended_path=recommended_path),
            "target": target,
            "nodes": nodes,
            "analysis": analysis,
            "stop_reason": stop_reason,
            "score_percent": round(float((target or {}).get("mastery_score") or 0.0) * 100),
            "confidence_percent": round(float((target or {}).get("confidence") or 0.0) * 100),
            "overall_mastery_percent": analysis["overall_mastery_percent"],
            "recommended_path": recommended_path,
            "path_options": PATH_OPTIONS,
        }

        for node in nodes:
            concept_id = node.get("concept_id")
            if concept_id and node.get("status") != "not_tested":
                _upsert_concept_state(session, user=user, node=node)

        assessment.status = "completed"
        assessment.completed_at = datetime.now(UTC)
        assessment.decision_state_json = {**state, "stop_reason": stop_reason}
        goal = session.get(LearningGoal, assessment.learning_goal_id) if assessment.learning_goal_id else None
        if goal is not None and goal.status != "in_progress":
            goal.status = "diagnosed"
            goal.metadata_json = {**(goal.metadata_json or {}), "diagnosis": diagnosis}
        if goal is not None:
            auto_session_goal = _auto_prepare_session_goal_from_diagnosis(
                session,
                user=user,
                goal=goal,
                recommended_path=recommended_path,
            )
            if auto_session_goal is not None:
                focus_concept_id = auto_session_goal.get("focus_concept_id")
                if focus_concept_id:
                    try:
                        goal.target_concept_id = UUID(str(focus_concept_id))
                    except ValueError:
                        pass
                diagnosis["session_goal"] = auto_session_goal
                goal.metadata_json = {
                    **(goal.metadata_json or {}),
                    "session_goal": auto_session_goal,
                }
        session.commit()
        return diagnosis


def _diagnosis_nodes(
    *,
    graph_scope: dict[str, Any],
    state: dict[str, Any],
) -> list[dict[str, Any]]:
    node_results = state.get("node_results", {})
    rows: list[dict[str, Any]] = []
    for node in graph_scope.get("nodes", []):
        if not isinstance(node, dict):
            continue
        concept_code = str(node.get("concept_code"))
        result = node_results.get(concept_code, {}) if isinstance(node_results, dict) else {}
        status = str(result.get("status", "not_tested"))
        mastery = _mastery(status)
        attempts = result.get("attempts", []) if isinstance(result, dict) else []
        evidence_summary = _evidence_summary(attempts)
        metric_summary = _metric_summary(
            attempts=attempts,
            mastery_score=mastery,
            confidence=_node_confidence(attempts),
        )
        rows.append(
            {
                "concept_id": node.get("concept_id"),
                "concept_code": concept_code,
                "title": node.get("title"),
                "role": node.get("role"),
                "depth": node.get("depth"),
                "status": status,
                "mastery_score": mastery,
                "confidence": _node_confidence(attempts),
                "difficulty_reached": _difficulty_reached(result),
                "evidence": attempts,
                "evidence_summary": evidence_summary,
                "answer_percent": metric_summary["answer_percent"],
                "evidence_percent": metric_summary["evidence_percent"],
                "score_percent": metric_summary["score_percent"],
                "confidence_percent": metric_summary["confidence_percent"],
                "metric_source": "adaptive_pretest_diagnosis",
            }
        )
    return rows


def _recommended_path(*, nodes: list[dict[str, Any]], stop_reason: str) -> str:
    if stop_reason == "target_ready":
        return "review_only"
    if stop_reason == "target_reinforcement":
        return "target_reinforcement"
    target = next((node for node in nodes if node["role"] == "target"), {})
    target_status = target.get("status")
    prerequisite_statuses = [
        node.get("status")
        for node in nodes
        if node.get("role") == "prerequisite" and node.get("status") != "not_tested"
    ]
    if any(status == "gap" for status in prerequisite_statuses):
        deepest_gap = any(
            node.get("status") == "gap" and int(node.get("depth") or 0) >= 2
            for node in nodes
        )
        return "full_foundation_path" if deepest_gap else "repair_prerequisites"
    if any(status in {"fragile", "partial"} for status in prerequisite_statuses):
        return "repair_prerequisites"
    if target_status == "fragile":
        return "target_from_basics"
    if target_status == "gap":
        return "target_intro"
    return "target_reinforcement"


def _upsert_concept_state(
    session: Session,
    *,
    user: UserAccount,
    node: dict[str, Any],
) -> None:
    concept = session.get(KnowledgeConcept, UUID(str(node["concept_id"])))
    if concept is None:
        return
    state = session.scalar(
        select(LearnerConceptState).where(
            LearnerConceptState.user_id == user.id,
            LearnerConceptState.concept_id == concept.id,
        )
    )
    if state is None:
        state = LearnerConceptState(
            user_id=user.id,
            concept_id=concept.id,
            status="ready",
            mastery_score=0.0,
            confidence_score=0.0,
            evidence_count=0,
        )
        session.add(state)
    status = str(node.get("status"))
    state.mastery_score = float(node.get("mastery_score") or 0.0)
    state.confidence_score = float(node.get("confidence") or 0.0)
    state.status = {
        "ready": "ready",
        "partial": "review_due",
        "fragile": "review_due",
        "gap": "gap",
        "probably_ready": "ready",
        "probably_gap": "gap",
    }.get(status, "review_due")
    state.evidence_count = state.evidence_count + len(node.get("evidence") or [])
    state.last_evaluated_at = datetime.now(UTC)
    state.next_review_at = datetime.now(UTC) + (
        timedelta(days=3) if state.status == "ready" else timedelta(days=1)
    )


def _mastery(status: str) -> float:
    return {
        "ready": 0.9,
        "partial": 0.62,
        "fragile": 0.45,
        "gap": 0.18,
        "probably_ready": 0.72,
        "probably_gap": 0.28,
        "not_tested": 0.0,
    }.get(status, 0.0)


def _node_confidence(attempts: object) -> float:
    if not isinstance(attempts, list) or not attempts:
        return 0.0
    values = [float(item.get("confidence", 0.0)) for item in attempts if isinstance(item, dict)]
    return round(sum(values) / max(1, len(values)), 4)


def _evidence_summary(attempts: object) -> dict[str, Any]:
    if not isinstance(attempts, list) or not attempts:
        return {
            "attempt_count": 0,
            "correct_count": 0,
            "avg_evidence_score": 0.0,
            "avg_reasoning_score": None,
            "reasoning_quality": "not_provided",
            "diagnostic_signals": [],
            "answered_difficulties": [],
            "careless_mistake_possible": False,
            "misconception_detected": False,
        }
    rows = [item for item in attempts if isinstance(item, dict)]
    evidence_values = [float(item.get("evidence_score", 0.0)) for item in rows]
    reasoning_values = [
        float(item["reasoning_score"])
        for item in rows
        if item.get("reasoning_score") is not None
    ]
    signals = [
        str(item.get("diagnostic_signal") or "")
        for item in rows
        if str(item.get("diagnostic_signal") or "").strip()
    ]
    reasoning_avg = (
        round(sum(reasoning_values) / len(reasoning_values), 4)
        if reasoning_values
        else None
    )
    return {
        "attempt_count": len(rows),
        "correct_count": sum(1 for item in rows if item.get("is_correct") is True),
        "avg_evidence_score": round(sum(evidence_values) / max(1, len(evidence_values)), 4),
        "avg_reasoning_score": reasoning_avg,
        "reasoning_quality": _reasoning_quality(reasoning_avg),
        "diagnostic_signals": list(dict.fromkeys(signals)),
        "answered_difficulties": list(dict.fromkeys(str(item.get("difficulty")) for item in rows)),
        "careless_mistake_possible": "possible_careless_mistake" in signals,
        "misconception_detected": "misconception_detected" in signals,
    }


def _metric_summary(
    *,
    attempts: object,
    mastery_score: float,
    confidence: float,
) -> dict[str, float]:
    rows = [item for item in attempts if isinstance(item, dict)] if isinstance(attempts, list) else []
    answer_values = [
        _attempt_score_value(item, key="answer_score", fallback=1.0 if item.get("is_correct") is True else 0.0)
        for item in rows
    ]
    evidence_values = [
        _attempt_score_value(item, key="evidence_score", fallback=answer_values[index] if index < len(answer_values) else 0.0)
        for index, item in enumerate(rows)
    ]
    answer_avg = sum(answer_values) / len(answer_values) if answer_values else 0.0
    evidence_avg = sum(evidence_values) / len(evidence_values) if evidence_values else 0.0
    return {
        "answer_percent": round(answer_avg * 100, 2),
        "evidence_percent": round(evidence_avg * 100, 2),
        "score_percent": round(float(mastery_score or 0.0) * 100, 2),
        "confidence_percent": round(float(confidence or 0.0) * 100, 2),
    }


def _attempt_score_value(item: dict[str, Any], *, key: str, fallback: float) -> float:
    try:
        return max(0.0, min(1.0, float(item.get(key, fallback))))
    except (TypeError, ValueError):
        return max(0.0, min(1.0, fallback))


def _difficulty_reached(result: dict[str, Any]) -> str | None:
    for difficulty in ("hard", "medium", "easy"):
        if result.get(difficulty) in {"correct", "wrong"}:
            return difficulty
    return None


def _summary(*, target: dict[str, Any] | None, recommended_path: str) -> str:
    title = str(target.get("title")) if target else "Target concept"
    return {
        "review_only": f"Kamu sudah siap di {title}; cukup review singkat.",
        "target_reinforcement": f"Kamu paham dasar {title}, tapi perlu latihan versi lebih sulit.",
        "target_from_basics": f"{title} mulai terbentuk, tapi belum stabil di level sedang.",
        "target_intro": f"{title} masih menjadi gap utama; mulai dari pengantar konsep.",
        "repair_prerequisites": f"Beberapa prasyarat {title} perlu diperkuat dulu.",
        "full_foundation_path": f"Fondasi sebelum {title} perlu dibangun ulang dari prasyarat terdalam.",
    }.get(recommended_path, f"Diagnosis {title} selesai.")


def _analysis_report(
    *,
    nodes: list[dict[str, Any]],
    target: dict[str, Any] | None,
    recommended_path: str,
    stop_reason: str,
) -> dict[str, Any]:
    tested_nodes = [node for node in nodes if node.get("status") != "not_tested"]
    strengths = [
        f"{node.get('title')} terlihat siap."
        for node in tested_nodes
        if node.get("status") in {"ready", "probably_ready"}
    ]
    gaps = [
        f"{node.get('title')} masih {node.get('status')}."
        for node in tested_nodes
        if node.get("status") in {"gap", "fragile", "partial", "probably_gap"}
    ]
    evidence_notes: list[str] = []
    for node in tested_nodes:
        summary = node.get("evidence_summary") or {}
        title = node.get("title")
        if summary.get("misconception_detected"):
            evidence_notes.append(f"{title}: reasoning menunjukkan miskonsepsi, bukan sekadar salah pilih.")
        elif summary.get("careless_mistake_possible"):
            evidence_notes.append(f"{title}: jawaban MCQ salah, tapi reasoning cukup kuat; mungkin careless.")
        elif summary.get("reasoning_quality") == "not_provided":
            evidence_notes.append(f"{title}: tidak ada penjelasan langkah, confidence diagnosis lebih rendah.")
        elif summary.get("reasoning_quality") == "weak":
            evidence_notes.append(f"{title}: langkah pengerjaan masih lemah atau belum nyambung.")

    mastery_values = [
        float(node.get("mastery_score") or 0.0)
        for node in tested_nodes
    ]
    return {
        "target_status": target.get("status") if target else "unknown",
        "stop_reason": stop_reason,
        "overall_mastery_percent": round(
            (sum(mastery_values) / max(1, len(mastery_values))) * 100
        ),
        "strengths": strengths,
        "gaps": gaps,
        "evidence_notes": evidence_notes,
        "recommended_focus": _recommended_focus(recommended_path),
    }


def _auto_prepare_session_goal_from_diagnosis(
    session: Session,
    *,
    user: UserAccount,
    goal: LearningGoal,
    recommended_path: str,
) -> dict[str, Any] | None:
    selected_path = (
        recommended_path if recommended_path in TRACK_PATH_OPTIONS else "target_from_basics"
    )
    try:
        selection = TrackBuilderService().select_path(
            session,
            user=user,
            learning_goal_id=goal.id,
            path_option=selected_path,
        )
    except ValueError:
        return None
    if selection is None or not selection.modules:
        return None

    track = session.scalar(
        select(LearningTrack)
        .where(LearningTrack.id == selection.track_id, LearningTrack.user_id == user.id)
        .options(selectinload(LearningTrack.modules))
    )
    if track is None:
        return None

    modules = sorted(track.modules, key=lambda item: item.sort_order)
    primary_module = next(
        (item for item in modules if item.status in {"ready", "active"}),
        modules[0] if modules else None,
    )
    if primary_module is None:
        return None

    concept = (
        session.get(KnowledgeConcept, primary_module.concept_id)
        if primary_module.concept_id
        else None
    )

    workspace = session.scalar(
        select(WorkspaceSession)
        .where(
            WorkspaceSession.user_id == user.id,
            WorkspaceSession.track_id == track.id,
            WorkspaceSession.module_id == primary_module.id,
            WorkspaceSession.status == "active",
        )
        .order_by(WorkspaceSession.updated_at.desc(), WorkspaceSession.created_at.desc())
    )
    if workspace is None:
        workspace_metadata = {
            "source": "pretest_auto_workspace",
            "learning_flow": "5e_steam",
            "context_source": "adaptive_pretest_primary_node",
            "active_node_id": concept.code if concept else None,
            "active_concept_type": (
                str((concept.metadata_json or {}).get("concept_type") or "").strip().lower()
                if concept is not None
                else "general_steam"
            ),
            "active_prerequisites": [],
        }
        workspace = WorkspaceSession(
            user_id=user.id,
            track_id=track.id,
            module_id=primary_module.id,
            current_topic=primary_module.title,
            content_mode="chat",
            status="active",
            metadata_json={key: value for key, value in workspace_metadata.items() if value is not None},
        )
        session.add(workspace)
        session.flush()

    return {
        "learning_goal_id": str(goal.id),
        "track_id": str(track.id),
        "module_id": str(primary_module.id),
        "workspace_session_id": str(workspace.id),
        "subject_id": str(goal.subject_id),
        "focus_concept_id": str(concept.id) if concept else None,
        "focus_concept_code": concept.code if concept else None,
        "focus_title": concept.title if concept else primary_module.title,
        "learning_flow": "5e_steam",
        "path_option": selected_path,
    }


def _reasoning_quality(score: float | None) -> str:
    if score is None:
        return "not_provided"
    if score >= 0.75:
        return "strong"
    if score >= 0.45:
        return "partial"
    return "weak"


def _recommended_focus(recommended_path: str) -> list[str]:
    return {
        "review_only": ["Review singkat target", "Latihan cepat level hard"],
        "target_reinforcement": ["Latihan target level medium-hard", "Bahas pola kesalahan"],
        "target_from_basics": ["Mulai target dari easy", "Naik bertahap ke medium"],
        "target_intro": ["Pengantar konsep target", "Contoh konkret sebelum latihan"],
        "repair_prerequisites": ["Perbaiki prerequisite yang gagal", "Lanjutkan target setelah prerequisite stabil"],
        "full_foundation_path": ["Bangun ulang prerequisite terdalam", "Susun ulang jalur dari fondasi"],
    }.get(recommended_path, ["Lanjutkan latihan adaptif"])

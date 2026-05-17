from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.modules.pretests.graph_scope_builder import direct_prerequisites


class PretestDecisionEngine:
    def record_attempt(
        self,
        state: dict[str, Any],
        *,
        concept_code: str,
        difficulty: str,
        is_correct: bool,
        evidence_score: float,
        confidence: float,
        answer_score: float | None = None,
        reasoning_score: float | None = None,
        canvas_score: float | None = None,
        diagnostic_signal: str = "",
        reasoning_signal: str = "",
    ) -> dict[str, Any]:
        next_state = deepcopy(state)
        node_results = next_state.setdefault("node_results", {})
        node_state = node_results.setdefault(
            concept_code,
            {"status": "not_asked", "attempts": []},
        )
        node_state[difficulty] = "correct" if is_correct else "wrong"
        node_state["attempts"].append(
            {
                "difficulty": difficulty,
                "is_correct": is_correct,
                "answer_score": round(float(answer_score if answer_score is not None else (1.0 if is_correct else 0.0)), 4),
                "reasoning_score": round(float(reasoning_score), 4) if reasoning_score is not None else None,
                "canvas_score": round(float(canvas_score), 4) if canvas_score is not None else None,
                "evidence_score": round(float(evidence_score), 4),
                "confidence": round(float(confidence), 4),
                "diagnostic_signal": diagnostic_signal,
                "reasoning_signal": reasoning_signal,
            }
        )
        node_state["status"] = _node_status(node_state)
        next_state["confidence"] = max(float(next_state.get("confidence", 0.0)), float(confidence))
        return next_state

    def decide(
        self,
        state: dict[str, Any],
        *,
        last_concept_code: str,
        last_difficulty: str,
        last_is_correct: bool,
        graph_scope: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        next_state = deepcopy(state)
        limit_action = self._limit_action(next_state)
        if limit_action is not None:
            next_state["stop_reason"] = limit_action["reason"]
            return next_state, limit_action

        target_code = str(next_state["target_concept_code"])
        if last_concept_code == target_code:
            return self._decide_target(
                next_state,
                last_difficulty=last_difficulty,
                last_is_correct=last_is_correct,
                graph_scope=graph_scope,
            )
        return self._decide_prerequisite(
            next_state,
            last_concept_code=last_concept_code,
            last_difficulty=last_difficulty,
            last_is_correct=last_is_correct,
            graph_scope=graph_scope,
        )

    def _decide_target(
        self,
        state: dict[str, Any],
        *,
        last_difficulty: str,
        last_is_correct: bool,
        graph_scope: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        target = str(state["target_concept_code"])
        if last_difficulty == "medium":
            return state, _ask(target, "hard" if last_is_correct else "easy", "target_medium_correct" if last_is_correct else "target_medium_wrong")
        if last_difficulty == "hard":
            reason = "target_ready" if last_is_correct else "target_reinforcement"
            state["stop_reason"] = reason
            return state, {"type": "finalize", "reason": reason}
        if last_difficulty == "easy":
            return self._ask_next_prerequisite(state, graph_scope=graph_scope, fallback_reason="target_basic_checked")
        state["stop_reason"] = "unsupported_target_difficulty"
        return state, {"type": "finalize", "reason": "unsupported_target_difficulty"}

    def _decide_prerequisite(
        self,
        state: dict[str, Any],
        *,
        last_concept_code: str,
        last_difficulty: str,
        last_is_correct: bool,
        graph_scope: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if last_difficulty == "medium":
            return state, _ask(
                last_concept_code,
                "hard" if last_is_correct else "easy",
                "prerequisite_medium_correct" if last_is_correct else "prerequisite_medium_wrong",
            )
        if last_difficulty == "hard":
            return self._ask_next_prerequisite(
                state,
                graph_scope=graph_scope,
                fallback_reason="prerequisite_strength_checked",
            )
        if last_difficulty == "easy":
            if not last_is_correct:
                self._boost_direct_prerequisites(state, graph_scope=graph_scope, concept_code=last_concept_code)
            return self._ask_next_prerequisite(
                state,
                graph_scope=graph_scope,
                fallback_reason="root_gap_found" if not last_is_correct else "root_fragility_found",
            )
        state["stop_reason"] = "unsupported_prerequisite_difficulty"
        return state, {"type": "finalize", "reason": "unsupported_prerequisite_difficulty"}

    def _ask_next_prerequisite(
        self,
        state: dict[str, Any],
        *,
        graph_scope: dict[str, Any],
        fallback_reason: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        queue = list(state.get("probe_queue", []))
        visited = set(state.get("node_results", {}).keys())
        target = str(state.get("target_concept_code"))
        visited.add(target)
        while queue:
            queue.sort(key=lambda item: (-float(item.get("priority", 0)), int(item.get("depth", 0)), str(item.get("concept_code"))))
            candidate = queue.pop(0)
            concept_code = str(candidate.get("concept_code"))
            if concept_code in visited:
                continue
            if len(visited) >= int(state.get("max_nodes_visited", 5)):
                state["probe_queue"] = queue
                state["stop_reason"] = "max_nodes_visited"
                return state, {"type": "finalize", "reason": "max_nodes_visited"}
            state["probe_queue"] = queue
            return state, _ask(concept_code, "medium", "enter_prerequisite_node")
        state["probe_queue"] = []
        state["stop_reason"] = fallback_reason if graph_scope.get("nodes") else "graph_exhausted"
        return state, {"type": "finalize", "reason": state["stop_reason"]}

    def _boost_direct_prerequisites(
        self,
        state: dict[str, Any],
        *,
        graph_scope: dict[str, Any],
        concept_code: str,
    ) -> None:
        queue = list(state.get("probe_queue", []))
        queued = {str(item.get("concept_code")): item for item in queue}
        visited = set(state.get("node_results", {}).keys())
        for prereq in direct_prerequisites(graph_scope, concept_code=concept_code):
            code = str(prereq["concept_code"])
            if code in visited:
                continue
            existing = queued.get(code)
            if existing is None:
                queue.append(prereq)
            else:
                existing["priority"] = max(float(existing.get("priority", 0)), float(prereq["priority"]))
        state["probe_queue"] = queue

    def _limit_action(self, state: dict[str, Any]) -> dict[str, Any] | None:
        if int(state.get("question_count", 0)) >= int(state.get("max_questions", 10)):
            return {"type": "finalize", "reason": "max_questions_reached"}
        if float(state.get("confidence", 0.0)) >= float(state.get("confidence_threshold", 0.8)):
            # Target mastery has explicit stop rules; confidence stops only after prerequisite probing starts.
            if str(state.get("current_concept_code")) != str(state.get("target_concept_code")):
                return {"type": "finalize", "reason": "confidence_threshold_reached"}
        return None


def _ask(concept_code: str, difficulty: str, reason: str) -> dict[str, Any]:
    return {
        "type": "next_question",
        "concept_code": concept_code,
        "difficulty": difficulty,
        "reason": reason,
    }


def _node_status(node_state: dict[str, Any]) -> str:
    medium = node_state.get("medium")
    hard = node_state.get("hard")
    easy = node_state.get("easy")
    if medium == "correct" and hard == "correct":
        return "ready"
    if medium == "correct" and hard == "wrong":
        return "partial"
    if medium == "wrong" and easy == "correct":
        return "fragile"
    if medium == "wrong" and easy == "wrong":
        return "gap"
    if medium == "correct":
        return "probably_ready"
    if medium == "wrong":
        return "probably_gap"
    return "not_asked"

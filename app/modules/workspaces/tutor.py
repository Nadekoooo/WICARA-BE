from __future__ import annotations

import logging
from typing import Any

from app.modules.ai import ai_client
from app.modules.ai.errors import AIError
from app.modules.ai.schemas import AIGenerationResponse
from app.modules.workspaces.models import WorkspaceEvent, WorkspaceSession
from app.modules.workspaces.schemas import TutorResponseRead

logger = logging.getLogger(__name__)

PROMPT_VERSION = "wicara_5e_v1"

_SYSTEM_INSTRUCTION = """
You are Wicara, a Socratic AI tutor for a STEAM learning platform.
Guide students using the 5E learning model: Engage, Explore, Explain, Elaborate, Evaluate.
Rules:
- Respond in the same language as the student (Bahasa Indonesia or English).
- Be concise: 1-3 sentences for chat, longer for explanations.
- End with one guiding question or clear next action.
- Never give away the full answer — lead the student to discover it.
- Be warm, encouraging, and precise.
""".strip()

_PROMPTS: dict[str, str] = {
    "engage": (
        "Topic: {topic}\n"
        "Stage: Engage\n\n"
        "Write a short opening (2-3 sentences) that sparks curiosity about this topic. "
        "Connect it to a real-world situation. End with one open question to activate prior knowledge. "
        "Do NOT explain the concept yet."
    ),
    "explore": (
        "Topic: {topic}\n"
        "Stage: Explore\n"
        "Conversation so far:\n{history}\n\n"
        "Student: {message}\n\n"
        "Give a probing challenge or small experiment that pushes the student to discover the answer. "
        "Keep it to 1-2 sentences."
    ),
    "explain": (
        "Topic: {topic}\n"
        "Stage: Explain\n"
        "Conversation so far:\n{history}\n\n"
        "Student: {message}\n\n"
        "Give a clear explanation: what it is, why it matters, one worked example, one analogy. "
        "Use short paragraphs. End with 'Does that make sense so far?'"
    ),
    "elaborate": (
        "Topic: {topic}\n"
        "Stage: Elaborate\n"
        "Conversation so far:\n{history}\n\n"
        "Student: {message}\n\n"
        "Give a practice task or extension question that makes the student apply what they learned. "
        "Keep it to 2-3 sentences."
    ),
    "evaluate": (
        "Topic: {topic}\n"
        "Stage: Evaluate\n"
        "Conversation so far:\n{history}\n\n"
        "Student answer: {message}\n\n"
        "If correct or partially correct: affirm and correct gently, suggest a next step. "
        "If incorrect: give a hint without revealing the answer. Ask them to try again. "
        "Keep it to 2-3 sentences."
    ),
    "chat": (
        "Topic: {topic}\n"
        "Conversation so far:\n{history}\n\n"
        "Student: {message}\n\n"
        "Respond as a Socratic tutor. Be concise (1-3 sentences). "
        "End with a guiding question or next action suggestion."
    ),
}

_STAGE_INTENT: dict[str, str] = {
    "engage": "spark_curiosity",
    "explore": "probe_understanding",
    "explain": "explain",
    "elaborate": "recommend_practice",
    "evaluate": "evaluate_response",
    "chat": "ask_followup",
}

_STAGE_ACTIONS: dict[str, list[str]] = {
    "engage": ["explore_topic", "ask_question", "use_canvas"],
    "explore": ["try_answer", "ask_clarification", "use_canvas"],
    "explain": ["summarize", "answer_quiz", "use_canvas"],
    "elaborate": ["apply_concept", "answer_quiz"],
    "evaluate": ["review_explanation", "retry_quiz", "continue_next_module"],
    "chat": ["ask_followup", "use_canvas", "answer_quiz"],
}


def _build_history(events: list[WorkspaceEvent], max_turns: int = 10) -> str:
    recent = events[-(max_turns * 2):]
    lines: list[str] = []
    for event in recent:
        text = event.text_payload.strip()
        if not text:
            continue
        role = "Student" if event.actor_type == "learner" else "Tutor"
        lines.append(f"{role}: {text}")
    return "\n".join(lines) if lines else "(no prior conversation)"


def _infer_stage(events: list[WorkspaceEvent], event_type: str) -> str:
    if event_type == "quiz_answer":
        return "evaluate"
    learner_turns = sum(
        1 for e in events if e.actor_type == "learner" and e.text_payload.strip()
    )
    if learner_turns == 0:
        return "engage"
    if learner_turns <= 2:
        return "explore"
    if learner_turns <= 5:
        return "explain"
    if learner_turns <= 9:
        return "elaborate"
    return "evaluate"


def _build_user_instruction(stage: str, topic: str, history: str, message: str) -> str:
    template = _PROMPTS.get(stage, _PROMPTS["chat"])
    return template.format(topic=topic, history=history, message=message)


async def generate_tutor_response(
    workspace: WorkspaceSession,
    event_type: str,
    text_payload: str,
    events: list[WorkspaceEvent],
) -> tuple[TutorResponseRead | None, dict[str, Any]]:
    """
    Call Gemini to generate a tutor response.
    Returns (TutorResponseRead | None, audit_metadata).
    Falls back to deterministic response if Gemini fails.
    Only returns a response for event types that warrant one.
    """
    if event_type not in {"text", "quiz_answer", "canvas_sent"}:
        return None, {"ai_source": "skipped", "reason": f"no_response_for_{event_type}"}

    topic = workspace.current_topic or "this module"
    history = _build_history(events)
    stage = _infer_stage(events, event_type)

    if event_type == "canvas_sent":
        stage = "explore"

    user_instruction = _build_user_instruction(
        stage=stage,
        topic=topic,
        history=history,
        message=text_payload or "(no message)",
    )

    audit: dict[str, Any] = {
        "prompt_version": PROMPT_VERSION,
        "stage": stage,
        "topic": topic,
        "event_type": event_type,
        "history_turns": history.count("\n") + 1,
    }

    try:
        ai_response: AIGenerationResponse = await ai_client.generate(
            system_instruction=_SYSTEM_INSTRUCTION,
            user_instruction=user_instruction,
        )
        audit.update(
            {
                "ai_source": "gemini",
                "ai_provider": ai_response.provider,
                "ai_model": ai_response.model,
                "finish_reason": ai_response.finish_reason,
                "input_tokens": ai_response.usage.input_tokens if ai_response.usage else None,
                "output_tokens": ai_response.usage.output_tokens if ai_response.usage else None,
            }
        )
        tutor_text = ai_response.text.strip()
        if not tutor_text:
            tutor_text = _fallback_text(event_type)
            audit["ai_source"] = "gemini_empty_fallback"

        return TutorResponseRead(
            text=tutor_text,
            intent=_STAGE_INTENT.get(stage, "ask_followup"),
            next_actions=_STAGE_ACTIONS.get(stage, ["ask_followup"]),
        ), audit

    except AIError as exc:
        logger.warning("Gemini tutor call failed, using deterministic fallback: %s", exc)
        audit["ai_source"] = "deterministic_fallback"
        audit["fallback_reason"] = str(exc)
        return _fallback_response(event_type, text_payload), audit


def _fallback_text(event_type: str) -> str:
    if event_type == "text":
        return (
            "That's a good thought. Try connecting it to the module concept, "
            "then use the canvas if a diagram would help clarify your reasoning."
        )
    if event_type == "canvas_sent":
        return (
            "I saved your canvas snapshot. Now write one sentence explaining "
            "what the sketch proves or shows."
        )
    if event_type == "quiz_answer":
        return (
            "I recorded your answer. Review the core concept and try the quiz again if needed."
        )
    return "I recorded that. Keep exploring the topic."


def _fallback_response(event_type: str, text_payload: str) -> TutorResponseRead:
    stage = "chat"
    if event_type == "quiz_answer":
        stage = "evaluate"
    elif event_type == "canvas_sent":
        stage = "explore"
    elif text_payload.strip():
        stage = "chat"

    return TutorResponseRead(
        text=_fallback_text(event_type),
        intent=_STAGE_INTENT.get(stage, "ask_followup"),
        next_actions=_STAGE_ACTIONS.get(stage, ["ask_followup"]),
    )

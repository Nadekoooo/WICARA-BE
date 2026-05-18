from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


_WORD_RE = re.compile(r"\S+")
_PUNCT_PAUSE_RE = re.compile(r"[,.!?;:]")


@dataclass(frozen=True)
class TemplateQualityIssue:
    path: str
    message: str
    severity: str  # "error" | "warning"
    code: str


@dataclass(frozen=True)
class TemplateQualityResult:
    passed: bool
    errors: list[TemplateQualityIssue]
    warnings: list[TemplateQualityIssue]
    metrics: dict[str, Any]

    def to_feedback_details(self) -> list[dict[str, Any]]:
        details: list[dict[str, Any]] = []
        for issue in self.errors + self.warnings:
            details.append(
                {
                    "path": issue.path,
                    "message": issue.message,
                    "type": f"quality_{issue.severity}",
                    "code": issue.code,
                    "severity": issue.severity,
                }
            )
        return details


def evaluate_template_quality(*, template_id: str, spec_json: dict[str, Any]) -> TemplateQualityResult:
    language = _normalize_language(spec_json.get("language"))
    audience = _normalize_audience_level(spec_json.get("audience_level"))

    steps = spec_json.get("steps")
    steps_list = steps if isinstance(steps, list) else []
    step_count = len(steps_list)

    narration_segments = spec_json.get("narration_segments")
    segments = narration_segments if isinstance(narration_segments, list) else []

    step_segment_map: dict[int, list[str]] = {}
    intro_parts: list[str] = [_clean_text(spec_json.get("intro_narration"))]
    summary_parts: list[str] = [_clean_text(spec_json.get("summary_narration"))]
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        slot = str(segment.get("slot", "")).strip().lower()
        text = _clean_text(segment.get("text"))
        if not text:
            continue
        if slot == "intro":
            intro_parts.append(text)
        elif slot in {"summary", "outro"}:
            summary_parts.append(text)
        elif slot == "step":
            raw_idx = segment.get("step_index")
            try:
                idx = int(raw_idx)
            except (TypeError, ValueError):
                continue
            if idx < 1:
                continue
            step_segment_map.setdefault(idx, []).append(text)

    step_narrations: list[str] = []
    for i, step in enumerate(steps_list, start=1):
        parts: list[str] = []
        if isinstance(step, dict):
            parts.append(_clean_text(step.get("narration")))
        parts.extend(step_segment_map.get(i, []))
        merged = _merge_unique(parts)
        step_narrations.append(merged)

    intro_text = _merge_unique(intro_parts)
    summary_text = _merge_unique(summary_parts)
    voiceover_script = _clean_text(spec_json.get("voiceover_script"))

    intro_seconds = _estimate_speech_seconds(intro_text, language)
    summary_seconds = _estimate_speech_seconds(summary_text, language)
    step_seconds = [_estimate_speech_seconds(text, language) for text in step_narrations]
    step_total_seconds = sum(step_seconds)

    estimated_total_seconds = intro_seconds + summary_seconds + step_total_seconds
    if estimated_total_seconds <= 0 and voiceover_script:
        estimated_total_seconds = _estimate_speech_seconds(voiceover_script, language)

    intro_ratio = _safe_ratio(intro_seconds, estimated_total_seconds)
    summary_ratio = _safe_ratio(summary_seconds, estimated_total_seconds)
    step_ratio = _safe_ratio(step_total_seconds, estimated_total_seconds)
    avg_step_seconds = (step_total_seconds / step_count) if step_count else 0.0

    issues: list[TemplateQualityIssue] = []

    if step_count < 2:
        issues.append(
            TemplateQualityIssue(
                path="steps",
                message="At least 2 steps are required for pedagogical pacing quality.",
                severity="error",
                code="insufficient_steps",
            )
        )

    for idx, text in enumerate(step_narrations, start=1):
        if text:
            continue
        issues.append(
            TemplateQualityIssue(
                path=f"steps.{idx - 1}.narration",
                message="Each step should have narration or mapped step narration_segments.",
                severity="error",
                code="missing_step_narration",
            )
        )

    if estimated_total_seconds > 0:
        if intro_ratio > 0.55:
            issues.append(
                TemplateQualityIssue(
                    path="intro_narration",
                    message="Intro narration is too dominant (>55% of estimated narration time).",
                    severity="error",
                    code="intro_too_long",
                )
            )
        elif intro_ratio > 0.45:
            issues.append(
                TemplateQualityIssue(
                    path="intro_narration",
                    message="Intro narration is long; distribute more explanation to steps.",
                    severity="warning",
                    code="intro_long_warning",
                )
            )

        if step_ratio < 0.35:
            issues.append(
                TemplateQualityIssue(
                    path="steps",
                    message="Step narration is too short (<35% of estimated narration time).",
                    severity="error",
                    code="steps_too_short",
                )
            )
        elif step_ratio < 0.50:
            issues.append(
                TemplateQualityIssue(
                    path="steps",
                    message="Step narration should carry more of the explanation (recommended >=50%).",
                    severity="warning",
                    code="steps_short_warning",
                )
            )

        if summary_ratio > 0.40:
            issues.append(
                TemplateQualityIssue(
                    path="summary_narration",
                    message="Summary narration is too dominant; keep summary concise.",
                    severity="warning",
                    code="summary_too_long",
                )
            )

    min_avg_step = _minimum_avg_step_seconds(audience)
    if step_count > 0 and avg_step_seconds < (min_avg_step * 0.75):
        issues.append(
            TemplateQualityIssue(
                path="steps",
                message=(
                    f"Average step narration duration is too short for {audience} "
                    f"(estimated {avg_step_seconds:.1f}s, target >= {min_avg_step:.1f}s)."
                ),
                severity="error",
                code="avg_step_too_short",
            )
        )
    elif step_count > 0 and avg_step_seconds < min_avg_step:
        issues.append(
            TemplateQualityIssue(
                path="steps",
                message=(
                    f"Average step narration duration is below recommended {min_avg_step:.1f}s "
                    f"for {audience}."
                ),
                severity="warning",
                code="avg_step_below_recommendation",
            )
        )

    min_total = _minimum_total_seconds(audience)
    if estimated_total_seconds > 0 and estimated_total_seconds < min_total:
        issues.append(
            TemplateQualityIssue(
                path="voiceover_script",
                message=(
                    f"Estimated narration length ({estimated_total_seconds:.1f}s) is shorter than "
                    f"recommended minimum for {audience} ({min_total:.1f}s)."
                ),
                severity="warning",
                code="total_duration_short_warning",
            )
        )

    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    metrics = {
        "template_id": template_id,
        "language": language,
        "audience_level": audience,
        "step_count": step_count,
        "estimated_total_seconds": round(estimated_total_seconds, 2),
        "estimated_intro_seconds": round(intro_seconds, 2),
        "estimated_step_seconds_total": round(step_total_seconds, 2),
        "estimated_summary_seconds": round(summary_seconds, 2),
        "intro_ratio": round(intro_ratio, 4),
        "step_ratio": round(step_ratio, 4),
        "summary_ratio": round(summary_ratio, 4),
        "avg_step_seconds": round(avg_step_seconds, 2),
    }
    return TemplateQualityResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        metrics=metrics,
    )


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_language(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if not normalized:
        return "en"
    aliases = {
        "indonesian": "id",
        "bahasa": "id",
        "english": "en",
    }
    normalized = aliases.get(normalized, normalized)
    if "-" in normalized:
        normalized = normalized.split("-", 1)[0] or normalized
    return normalized[:16] or "en"


def _normalize_audience_level(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"sd", "smp", "sma"}:
        return normalized
    if "elementary" in normalized:
        return "sd"
    if "middle" in normalized or "junior" in normalized:
        return "smp"
    if "high" in normalized or "senior" in normalized:
        return "sma"
    return "smp"


def _merge_unique(parts: list[str]) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for raw in parts:
        text = _clean_text(raw)
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return " ".join(out).strip()


def _estimate_speech_seconds(text: str, language: str) -> float:
    cleaned = _clean_text(text)
    if not cleaned:
        return 0.0
    word_count = len(_WORD_RE.findall(cleaned))
    punctuation_count = len(_PUNCT_PAUSE_RE.findall(cleaned))
    words_per_second = _words_per_second(language)
    base_seconds = (word_count / words_per_second) if words_per_second > 0 else 0.0
    pause_seconds = punctuation_count * 0.14
    return max(0.0, base_seconds + pause_seconds)


def _words_per_second(language: str) -> float:
    if language == "id":
        return 2.35
    if language == "en":
        return 2.50
    return 2.30


def _safe_ratio(part: float, total: float) -> float:
    if total <= 0:
        return 0.0
    return max(0.0, part / total)


def _minimum_avg_step_seconds(audience_level: str) -> float:
    if audience_level == "sd":
        return 5.5
    if audience_level == "smp":
        return 4.5
    if audience_level == "sma":
        return 4.0
    return 4.5


def _minimum_total_seconds(audience_level: str) -> float:
    if audience_level == "sd":
        return 35.0
    if audience_level == "smp":
        return 45.0
    if audience_level == "sma":
        return 55.0
    return 45.0

from __future__ import annotations

from typing import Any

import httpx

from app.modules.ai.config import AISettings
from app.modules.ai.errors import AIConfigurationError, AIProviderError
from app.modules.ai.providers.base import AIProvider
from app.modules.ai.schemas import (
    AIGenerationRequest,
    AIGenerationResponse,
    AIImageInput,
    AITextInput,
    AIUsage,
)


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, settings: AISettings) -> None:
        self._settings = settings

    async def generate(self, request: AIGenerationRequest) -> AIGenerationResponse:
        api_key = self._settings.gemini_api_key.strip()
        if not api_key:
            raise AIConfigurationError("GEMINI_API_KEY is missing.")

        payload = self._build_payload(request)
        endpoint = self._endpoint_for_model(request.model)
        try:
            async with httpx.AsyncClient(timeout=self._settings.ai_request_timeout_seconds) as client:
                response = await client.post(
                    endpoint,
                    params={"key": api_key},
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise AIProviderError(f"Gemini request failed: {exc}") from exc

        if response.status_code >= 400:
            raise AIProviderError(
                f"Gemini request failed with status {response.status_code}: "
                f"{_provider_error_message(response)}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise AIProviderError("Gemini response was not valid JSON.") from exc

        return self._response_from_payload(request, data)

    def _endpoint_for_model(self, model: str) -> str:
        model_path = model if "/" in model else f"models/{model}"
        return f"{self._settings.gemini_base_url.rstrip('/')}/{model_path}:generateContent"

    def _build_payload(self, request: AIGenerationRequest) -> dict[str, Any]:
        parts: list[dict[str, Any]] = []
        if request.user_instruction:
            parts.append({"text": request.user_instruction})

        for item in request.inputs:
            if isinstance(item, AITextInput):
                parts.append({"text": item.text})
            elif isinstance(item, AIImageInput):
                parts.append(
                    {
                        "inline_data": {
                            "mime_type": item.mime_type,
                            "data": item.as_base64(),
                        }
                    }
                )

        payload: dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": parts,
                }
            ]
        }
        if request.system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": request.system_instruction}],
            }

        generation_config = request.params.model_dump(by_alias=True, exclude_none=True)
        if generation_config:
            payload["generationConfig"] = generation_config
        return payload

    def _response_from_payload(
        self,
        request: AIGenerationRequest,
        data: dict[str, Any],
    ) -> AIGenerationResponse:
        candidates = data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            prompt_feedback = data.get("promptFeedback") or {}
            block_reason = prompt_feedback.get("blockReason")
            if block_reason:
                raise AIProviderError(f"Gemini blocked the prompt: {block_reason}")
            raise AIProviderError("Gemini returned no candidates.")

        first_candidate = candidates[0] if isinstance(candidates[0], dict) else {}
        text = _extract_candidate_text(first_candidate)
        if not text:
            finish_reason = first_candidate.get("finishReason")
            raise AIProviderError(
                f"Gemini returned no text."
                f"{f' Finish reason: {finish_reason}.' if finish_reason else ''}"
            )

        usage = _usage_from_payload(data.get("usageMetadata"))
        return AIGenerationResponse(
            provider=self.name,
            model=request.model,
            text=text,
            finish_reason=first_candidate.get("finishReason"),
            usage=usage,
            response_id=data.get("responseId"),
            raw=data,
        )


def _extract_candidate_text(candidate: dict[str, Any]) -> str:
    content = candidate.get("content") or {}
    parts = content.get("parts") or []
    text_parts = [
        str(part["text"])
        for part in parts
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    ]
    return "\n".join(text_parts).strip()


def _usage_from_payload(value: Any) -> AIUsage | None:
    if not isinstance(value, dict):
        return None
    return AIUsage(
        input_tokens=value.get("promptTokenCount"),
        output_tokens=value.get("candidatesTokenCount"),
        total_tokens=value.get("totalTokenCount"),
        raw=value,
    )


def _provider_error_message(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text.strip() or "No error body returned."

    error = data.get("error")
    if isinstance(error, dict):
        message = error.get("message")
        if message:
            return str(message)
    message = data.get("message")
    if message:
        return str(message)
    return str(data)

from __future__ import annotations

import base64
import binascii
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.ai.errors import AIInputError


class AITextInput(BaseModel):
    type: Literal["text"]
    text: str = Field(..., min_length=1)

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("Text input cannot be empty.")
        return text


class AIImageInput(BaseModel):
    type: Literal["image"]
    mime_type: str = Field(..., min_length=3)
    data: str | bytes | None = None
    file_path: str | None = None

    @field_validator("mime_type")
    @classmethod
    def validate_mime_type(cls, value: str) -> str:
        mime_type = value.strip().lower()
        if not mime_type.startswith("image/"):
            raise ValueError("Image input mime_type must start with image/.")
        return mime_type

    @model_validator(mode="after")
    def validate_payload_source(self) -> AIImageInput:
        has_data = self.data not in (None, "", b"")
        has_file_path = bool(self.file_path and self.file_path.strip())
        if has_data == has_file_path:
            raise ValueError("Image input requires exactly one of data or file_path.")
        if has_file_path:
            self.file_path = str(Path(self.file_path or "").expanduser())
        return self

    def as_base64(self) -> str:
        if self.file_path:
            try:
                return base64.b64encode(Path(self.file_path).read_bytes()).decode("ascii")
            except OSError as exc:
                raise AIInputError(f"Image file could not be read: {self.file_path}") from exc

        if isinstance(self.data, bytes):
            return base64.b64encode(self.data).decode("ascii")

        if isinstance(self.data, str):
            encoded = _strip_data_uri_prefix(self.data.strip())
            try:
                base64.b64decode(encoded, validate=True)
            except binascii.Error as exc:
                raise AIInputError("Image input data must be base64 encoded.") from exc
            return encoded

        raise AIInputError("Image input requires data or file_path.")


AIInput = Annotated[AITextInput | AIImageInput, Field(discriminator="type")]


class AIGenerationParams(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(
        default=None,
        gt=0,
        validation_alias=AliasChoices("max_tokens", "maxOutputTokens"),
    )
    top_p: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("top_p", "topP"),
    )
    top_k: int | None = Field(
        default=None,
        gt=0,
        validation_alias=AliasChoices("top_k", "topK"),
    )
    stop: str | list[str] | None = Field(
        default=None,
        validation_alias=AliasChoices("stop", "stopSequences"),
    )
    response_format: dict[str, Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("response_format", "responseFormat"),
    )


class AIGenerationRequest(BaseModel):
    provider: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    system_instruction: str | None = None
    user_instruction: str | None = None
    inputs: list[AIInput] = Field(default_factory=list)
    params: AIGenerationParams = Field(default_factory=AIGenerationParams)

    @field_validator("provider", "model")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("Value cannot be empty.")
        return text

    @field_validator("system_instruction", "user_instruction")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        text = value.strip()
        return text or None

    @model_validator(mode="after")
    def validate_content(self) -> AIGenerationRequest:
        if self.user_instruction is None and not self.inputs:
            raise ValueError("AI request requires user_instruction or at least one input.")
        return self


class AIUsage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class AIGenerationResponse(BaseModel):
    provider: str
    model: str
    text: str
    finish_reason: str | None = None
    usage: AIUsage | None = None
    response_id: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


def _strip_data_uri_prefix(value: str) -> str:
    if value.startswith("data:") and "," in value:
        return value.split(",", 1)[1].strip()
    return "".join(value.split())

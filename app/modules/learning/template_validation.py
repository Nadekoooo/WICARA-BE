from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.modules.learning.template_registry import (
    TemplateRegistryError,
    resolve_template_entry,
)


@dataclass(frozen=True)
class TemplateValidationResult:
    template_id: str
    normalized_spec: dict[str, Any]
    template_path: str
    scene_class: str
    schema_id: str
    resolved_from: str
    used_alias: bool


class TemplateValidationError(ValueError):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        details: list[dict[str, Any]] | None = None,
        template_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or []
        self.template_id = template_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "template_id": self.template_id,
            "details": self.details,
        }


class StepSpec(BaseModel):
    title: str = Field(..., min_length=1, max_length=140)
    body: str = Field(..., min_length=1, max_length=800)
    narration: str = Field(default="", max_length=1200)
    model_config = ConfigDict(extra="allow")


class NarrationSegmentSpec(BaseModel):
    slot: str = Field(default="intro", min_length=1, max_length=32)
    step_index: int | None = Field(default=None, ge=1, le=50)
    text: str = Field(..., min_length=1, max_length=1200)
    model_config = ConfigDict(extra="allow")


class BaseTemplateSpec(BaseModel):
    phase: str = Field(default="D", min_length=1, max_length=8)
    audience_level: str = Field(default="smp", min_length=1, max_length=16)
    title: str = Field(..., min_length=1, max_length=255)
    subtitle: str = Field(default="", max_length=255)
    steps: list[StepSpec] = Field(..., min_length=1, max_length=12)
    summary: str = Field(..., min_length=1, max_length=1200)
    voiceover_script: str = Field(default="", max_length=6000)
    intro_narration: str = Field(default="", max_length=1200)
    summary_narration: str = Field(default="", max_length=1200)
    narration_segments: list[NarrationSegmentSpec] = Field(default_factory=list, max_length=64)
    model_config = ConfigDict(extra="allow")


class NumberRangeSpec(BaseModel):
    min: float
    max: float
    step: float

    @model_validator(mode="after")
    def validate_range(self) -> NumberRangeSpec:
        if self.max <= self.min:
            raise ValueError("number_range.max must be greater than number_range.min.")
        if self.step <= 0:
            raise ValueError("number_range.step must be greater than zero.")
        return self


class MarkerSpec(BaseModel):
    value: float
    label: str = Field(..., min_length=1, max_length=40)
    model_config = ConfigDict(extra="allow")


class NumberLineOperationSpec(BaseModel):
    type: str = Field(default="compare", min_length=1, max_length=32)
    from_: float = Field(alias="from")
    to: float
    label: str = Field(default="", max_length=120)
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class NumberLineQuantitySpec(BaseTemplateSpec):
    number_range: NumberRangeSpec
    markers: list[MarkerSpec] = Field(..., min_length=1, max_length=12)
    highlight_values: list[float] = Field(default_factory=list)
    operation: NumberLineOperationSpec | None = None


class GroupingStepSpec(BaseModel):
    label: str = Field(..., min_length=1, max_length=120)
    value: float
    model_config = ConfigDict(extra="allow")


class ElementaryArithmeticBlocksSpec(BaseTemplateSpec):
    operation_type: str = Field(..., min_length=1, max_length=40)
    operands: list[float] = Field(..., min_length=2, max_length=8)
    blocks: dict[str, Any] = Field(default_factory=dict)
    grouping_steps: list[GroupingStepSpec] = Field(default_factory=list)
    result: float


class FractionValueSpec(BaseModel):
    numerator: int = Field(..., ge=0)
    denominator: int = Field(..., ge=1)
    label: str = Field(..., min_length=1, max_length=40)
    model_config = ConfigDict(extra="allow")


class FractionEquivalenceSpec(BaseModel):
    left: str = Field(..., min_length=1, max_length=40)
    right: str = Field(..., min_length=1, max_length=40)
    model_config = ConfigDict(extra="allow")


class FractionBarPartitionSpec(BaseTemplateSpec):
    representations: list[str] = Field(default_factory=list)
    fractions: list[FractionValueSpec] = Field(..., min_length=1, max_length=12)
    partition_count: int = Field(..., ge=1, le=200)
    highlight_parts: list[int] = Field(default_factory=list)
    equivalences: list[FractionEquivalenceSpec] = Field(default_factory=list)


class QuantitySpec(BaseModel):
    label: str = Field(..., min_length=1, max_length=50)
    value: float
    unit: str = Field(default="", max_length=32)
    model_config = ConfigDict(extra="allow")


class ScalingStepSpec(BaseModel):
    from_: str = Field(alias="from", min_length=1, max_length=64)
    to: str = Field(..., min_length=1, max_length=64)
    label: str = Field(default="", max_length=120)
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class RatioProportionSpec(BaseTemplateSpec):
    context: str = Field(default="", max_length=200)
    quantities: list[QuantitySpec] = Field(..., min_length=2, max_length=12)
    ratio_pairs: list[list[str]] = Field(default_factory=list)
    scale_factor: float
    scaling_steps: list[ScalingStepSpec] = Field(default_factory=list)


class EquationSolutionStepSpec(BaseModel):
    operation: str = Field(..., min_length=1, max_length=80)
    value: float
    left_result: str = Field(..., min_length=1, max_length=80)
    right_result: str = Field(..., min_length=1, max_length=80)
    explanation: str = Field(default="", max_length=220)
    model_config = ConfigDict(extra="allow")


class EquationBalanceSpec(BaseTemplateSpec):
    equation: str = Field(..., min_length=1, max_length=120)
    left_expression: str = Field(..., min_length=1, max_length=80)
    right_expression: str = Field(..., min_length=1, max_length=80)
    solution_steps: list[EquationSolutionStepSpec] = Field(..., min_length=1, max_length=12)
    final_solution: str = Field(..., min_length=1, max_length=80)


class SequenceTableValueSpec(BaseModel):
    n: int = Field(..., ge=1)
    value: float
    model_config = ConfigDict(extra="allow")


class SequenceTargetSpec(BaseModel):
    n: int = Field(..., ge=1)
    value: float
    model_config = ConfigDict(extra="allow")


class SequencePatternSpec(BaseTemplateSpec):
    terms: list[float] = Field(..., min_length=2, max_length=40)
    visual_pattern_type: str = Field(default="", max_length=80)
    rule: str = Field(..., min_length=1, max_length=220)
    table_values: list[SequenceTableValueSpec] = Field(default_factory=list)
    target_term: SequenceTargetSpec


class GraphFunctionSpec(BaseModel):
    type: str = Field(..., min_length=1, max_length=64)
    params: dict[str, float] = Field(default_factory=dict)
    model_config = ConfigDict(extra="allow")


class GraphFeatureSpec(BaseModel):
    type: str = Field(..., min_length=1, max_length=64)
    label: str = Field(default="", max_length=80)
    model_config = ConfigDict(extra="allow")


class HighlightPointSpec(BaseModel):
    x: float
    label: str = Field(default="", max_length=80)
    y: float | None = None
    model_config = ConfigDict(extra="allow")


class GraphExplanationSpec(BaseTemplateSpec):
    function: GraphFunctionSpec
    x_range: list[float] = Field(..., min_length=3, max_length=3)
    y_range: list[float] = Field(..., min_length=3, max_length=3)
    graph_features: list[GraphFeatureSpec] = Field(default_factory=list)
    highlight_points: list[HighlightPointSpec] = Field(default_factory=list)
    formula_latex: str = Field(default="", max_length=200)


class GeometryTransformationSpec(BaseModel):
    type: str = Field(..., min_length=1, max_length=80)
    label: str = Field(default="", max_length=120)
    model_config = ConfigDict(extra="allow")


class GeometryAreaVolumeSpec(BaseTemplateSpec):
    shape_type: str = Field(..., min_length=1, max_length=50)
    dimensions: dict[str, Any]
    transformations: list[GeometryTransformationSpec] = Field(default_factory=list)
    formula_latex: str = Field(default="", max_length=200)
    highlight_features: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dimensions(self) -> GeometryAreaVolumeSpec:
        numeric_keys = [
            key
            for key, value in self.dimensions.items()
            if key != "unit" and isinstance(value, (int, float))
        ]
        if not numeric_keys:
            raise ValueError("dimensions must include at least one numeric measure.")
        return self


class MotionKinematicsSpec(BaseTemplateSpec):
    scenario: str = Field(default="", max_length=220)
    time_points: list[float] = Field(..., min_length=2, max_length=200)
    position_data: list[float] = Field(..., min_length=2, max_length=200)
    velocity_data: list[float] = Field(default_factory=list)
    acceleration: float | int = 0
    graph_type: str = Field(default="", max_length=80)

    @model_validator(mode="after")
    def validate_lengths(self) -> MotionKinematicsSpec:
        if len(self.position_data) != len(self.time_points):
            raise ValueError("position_data length must match time_points length.")
        if self.velocity_data and len(self.velocity_data) != len(self.time_points):
            raise ValueError("velocity_data length must match time_points length.")
        return self


class ForceObjectSpec(BaseModel):
    type: str = Field(..., min_length=1, max_length=80)
    label: str = Field(..., min_length=1, max_length=80)
    model_config = ConfigDict(extra="allow")


class ForceVectorSpec(BaseModel):
    label: str = Field(..., min_length=1, max_length=40)
    magnitude: float
    unit: str = Field(..., min_length=1, max_length=20)
    direction: str = Field(..., min_length=1, max_length=20)
    model_config = ConfigDict(extra="allow")


class ResultantForceSpec(BaseModel):
    magnitude: float
    unit: str = Field(..., min_length=1, max_length=20)
    direction: str = Field(..., min_length=1, max_length=20)
    model_config = ConfigDict(extra="allow")


class ForceDiagramSpec(BaseTemplateSpec):
    object: ForceObjectSpec
    forces: list[ForceVectorSpec] = Field(..., min_length=1, max_length=20)
    resultant: ResultantForceSpec
    motion_response: str = Field(default="", max_length=300)
    force_scale: float = Field(default=0.2, gt=0)


_SCHEMA_MODEL_MAP: dict[str, type[BaseModel]] = {
    "manim.number_line_quantity.v1": NumberLineQuantitySpec,
    "manim.elementary_arithmetic_blocks.v1": ElementaryArithmeticBlocksSpec,
    "manim.fraction_bar_partition.v1": FractionBarPartitionSpec,
    "manim.ratio_proportion.v1": RatioProportionSpec,
    "manim.equation_balance.v1": EquationBalanceSpec,
    "manim.sequence_pattern.v1": SequencePatternSpec,
    "manim.geometry_area_volume.v1": GeometryAreaVolumeSpec,
    "manim.graph_explanation.v1": GraphExplanationSpec,
    "manim.motion_kinematics.v1": MotionKinematicsSpec,
    "manim.force_diagram.v1": ForceDiagramSpec,
}


def validate_template_spec(
    *,
    template_id: str,
    spec_json: dict[str, Any],
) -> TemplateValidationResult:
    if not isinstance(spec_json, dict):
        raise TemplateValidationError(
            code="validation_error",
            message="spec_json must be an object.",
            details=[{"path": "spec_json", "message": "Expected JSON object.", "type": "type_error"}],
        )

    try:
        resolved = resolve_template_entry(template_id)
    except TemplateRegistryError as exc:
        raise TemplateValidationError(
            code="unknown_template",
            message=str(exc),
            details=[{"path": "template_id", "message": str(exc), "type": "unknown_template"}],
        ) from exc

    schema_cls = _SCHEMA_MODEL_MAP.get(resolved.entry.schema_id)
    if schema_cls is None:
        raise TemplateValidationError(
            code="unknown_schema",
            message=f"No schema validator mapped for '{resolved.entry.schema_id}'.",
            details=[
                {
                    "path": "template_id",
                    "message": f"Missing schema mapping for {resolved.entry.schema_id}.",
                    "type": "unknown_schema",
                }
            ],
            template_id=resolved.entry.template_id,
        )

    payload = dict(spec_json)
    payload["template_id"] = resolved.entry.template_id
    try:
        validated = schema_cls.model_validate(payload)
    except ValidationError as exc:
        raise TemplateValidationError(
            code="validation_error",
            message="Template spec validation failed.",
            details=_validation_error_to_details(exc),
            template_id=resolved.entry.template_id,
        ) from exc

    normalized_spec = validated.model_dump(mode="python", by_alias=True)
    normalized_spec["template_id"] = resolved.entry.template_id

    return TemplateValidationResult(
        template_id=resolved.entry.template_id,
        normalized_spec=normalized_spec,
        template_path=resolved.entry.template_path,
        scene_class=resolved.entry.scene_class,
        schema_id=resolved.entry.schema_id,
        resolved_from=resolved.resolved_from,
        used_alias=resolved.used_alias,
    )


def _validation_error_to_details(exc: ValidationError) -> list[dict[str, str]]:
    details: list[dict[str, str]] = []
    for item in exc.errors():
        loc = item.get("loc", ())
        path = ".".join(str(part) for part in loc)
        details.append(
            {
                "path": path or "spec_json",
                "message": str(item.get("msg", "Invalid value.")),
                "type": str(item.get("type", "validation_error")),
            }
        )
    return details

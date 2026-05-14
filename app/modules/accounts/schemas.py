from __future__ import annotations

from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class SupabaseAuthRequest(BaseModel):
    access_token: str = Field(..., min_length=20)
    role: str = "learner"


class PasswordSignInRequest(BaseModel):
    email_or_phone: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)
    role: str = "learner"


class PasswordRegisterRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    display_name: str = ""
    role: str = "learner"


class GoogleSignInRequest(BaseModel):
    id_token: str = Field(..., min_length=20)
    access_token: str | None = None
    role: str = "learner"


class AuthSessionResponse(BaseModel):
    user_id: str
    display_name: str
    role: str
    token: str
    email: str | None = None
    onboarding_completed: bool = False


class UserAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    supabase_user_id: str
    email: str | None
    phone: str | None
    display_name: str
    role: str
    status: str


class LearnerProfileOnboardingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(default="", max_length=160)
    country_name: str = Field(
        default="",
        max_length=80,
        validation_alias=AliasChoices("country_name", "country"),
    )
    education_level: str = Field(default="", max_length=64)
    grade_level: str = Field(default="", max_length=64)
    preferred_language: str = Field(default="id", max_length=16)
    study_goal: str = ""
    daily_study_time_label: str = Field(
        default="",
        max_length=80,
        validation_alias=AliasChoices("daily_study_time_label", "daily_study_time"),
    )
    selected_subjects: list[str] = Field(default_factory=list)


class LearnerProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    full_name: str
    country_name: str
    education_level: str
    grade_level: str
    preferred_language: str
    study_goal: str
    daily_study_time_label: str
    selected_subjects: list[str]
    onboarding_completed: bool


class AccountProfileResponse(BaseModel):
    account: UserAccountRead
    profile: LearnerProfileRead | None = None
    onboarding_completed: bool

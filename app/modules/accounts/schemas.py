from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SupabaseAuthRequest(BaseModel):
    access_token: str = Field(..., min_length=20)
    role: str = "learner"


class PasswordSignInRequest(BaseModel):
    email_or_phone: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)
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
    full_name: str = Field(default="", max_length=160)
    country_name: str = Field(default="", max_length=80)
    grade_level: str = Field(default="", max_length=64)
    preferred_language: str = Field(default="id", max_length=16)
    study_goal: str = ""
    daily_study_time_label: str = Field(default="", max_length=80)
    selected_subjects: list[str] = Field(default_factory=list)


class LearnerProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    full_name: str
    country_name: str
    grade_level: str
    preferred_language: str
    study_goal: str
    daily_study_time_label: str
    selected_subjects: list[str]
    onboarding_completed: bool

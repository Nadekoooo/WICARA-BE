from __future__ import annotations

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

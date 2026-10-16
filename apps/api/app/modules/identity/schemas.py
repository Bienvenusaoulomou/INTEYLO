from datetime import datetime
from typing import Annotated
from uuid import UUID
from zoneinfo import available_timezones

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, StringConstraints

_TIMEZONES = available_timezones()


def _lower(value: str) -> str:
    return value.lower()


def _timezone(value: str) -> str:
    if value not in _TIMEZONES:
        raise ValueError("invalid_timezone")
    return value


Email = Annotated[EmailStr, AfterValidator(_lower)]
Password = Annotated[str, StringConstraints(min_length=12, max_length=128)]
FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
OrgName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=200)]
Timezone = Annotated[str, AfterValidator(_timezone)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SignupIn(StrictModel):
    email: Email
    password: Password
    full_name: FullName
    organization_name: OrgName
    timezone: Timezone = "UTC"


class LoginIn(StrictModel):
    email: Email
    password: Annotated[str, StringConstraints(min_length=1, max_length=128)]


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_platform_admin: bool


class OrganizationSummary(BaseModel):
    id: UUID
    name: str
    status: str


class MembershipOut(BaseModel):
    organization: OrganizationSummary
    roles: list[str]
    permissions: list[str]


class MeOut(BaseModel):
    user: UserOut
    memberships: list[MembershipOut]


class SessionOut(BaseModel):
    id: UUID
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    ip_address: str | None
    user_agent: str | None
    current: bool


class OkOut(BaseModel):
    ok: bool = True


class RevokedOut(BaseModel):
    revoked: int


class OrgUpdateIn(StrictModel):
    name: OrgName | None = None
    timezone: Timezone | None = None


class InvitationCreateIn(StrictModel):
    email: Email
    role: Annotated[str, StringConstraints(min_length=1, max_length=50)]


class RolesUpdateIn(StrictModel):
    roles: Annotated[
        list[Annotated[str, StringConstraints(max_length=50)]], Field(min_length=1, max_length=5)
    ]


class InvitationTokenIn(StrictModel):
    token: Annotated[str, StringConstraints(min_length=20, max_length=200)]


class InvitationAcceptIn(InvitationTokenIn):
    full_name: FullName | None = None
    password: Password | None = None

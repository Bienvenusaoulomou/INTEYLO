from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class OrganizationOut(BaseModel):
    id: UUID
    name: str
    status: str
    locale: str
    timezone: str
    created_at: datetime


class MemberUser(BaseModel):
    id: UUID
    email: str
    full_name: str


class MemberOut(BaseModel):
    membership_id: UUID
    user: MemberUser
    status: str
    roles: list[str]
    joined_at: datetime


class RoleOut(BaseModel):
    key: str
    rank: int
    permissions: list[str]
    assignable: bool


class InvitationOut(BaseModel):
    id: UUID
    email: str
    role: str
    status: str
    created_at: datetime
    expires_at: datetime
    invited_by_name: str | None


class InvitationCreatedOut(InvitationOut):
    accept_url: str


class InvitationPreviewOut(BaseModel):
    organization_name: str
    email: str
    role: str
    expires_at: datetime
    account_exists: bool


class AuditEventOut(BaseModel):
    id: UUID
    created_at: datetime
    action: str
    outcome: str
    actor_email: str | None
    target_type: str | None
    target_id: str | None
    details: dict[str, Any]
    ip_address: str | None


class AuditPageOut(BaseModel):
    items: list[AuditEventOut]
    limit: int
    offset: int

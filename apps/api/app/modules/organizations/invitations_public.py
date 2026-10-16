"""Consultation et acceptation d'une invitation à partir de son jeton."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from app.core.db import get_db, set_tenant_context
from app.core.errors import ApiError, ErrorCode
from app.core.security import hash_password, hash_token
from app.modules.audit.service import record
from app.modules.identity.deps import CurrentUser, client_ip, get_optional_user
from app.modules.identity.models import User
from app.modules.identity.schemas import InvitationAcceptIn, InvitationTokenIn, MeOut
from app.modules.identity.service import build_me, open_session
from app.modules.organizations.models import Invitation, Membership, MembershipRole, Organization
from app.modules.organizations.schemas import InvitationPreviewOut

router = APIRouter(prefix="/v1/invitations", tags=["invitations"])


def _load_valid_invitation(db: Session, token: str, user_id: object = None) -> Invitation:
    row = db.execute(
        text("select * from invitation_lookup(:h)"), {"h": hash_token(token)}
    ).one_or_none()
    if row is None:
        raise ApiError(ErrorCode.INVITATION_INVALID, 400)
    set_tenant_context(db, user_id=user_id, org_id=row.org_id)  # type: ignore[arg-type]
    inv = db.get(Invitation, row.invitation_id)
    now = datetime.now(UTC)
    if inv is None or inv.accepted_at or inv.revoked_at or inv.expires_at <= now:
        raise ApiError(ErrorCode.INVITATION_INVALID, 400)
    org = db.get(Organization, inv.org_id)
    if org is None or org.status != "active":
        raise ApiError(ErrorCode.INVITATION_INVALID, 400)
    return inv


@router.post("/inspect", response_model=InvitationPreviewOut)
def inspect_invitation(
    payload: InvitationTokenIn, db: Session = Depends(get_db)
) -> InvitationPreviewOut:
    inv = _load_valid_invitation(db, payload.token)
    org = db.get(Organization, inv.org_id)
    assert org is not None  # noqa: S101
    exists = db.scalar(select(User.id).where(User.email == inv.email)) is not None
    return InvitationPreviewOut(
        organization_name=org.name,
        email=inv.email,
        role=inv.role_key,
        expires_at=inv.expires_at,
        account_exists=exists,
    )


@router.post("/accept", response_model=MeOut)
def accept_invitation(
    payload: InvitationAcceptIn,
    request: Request,
    response: Response,
    current: CurrentUser | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> MeOut:
    ip = client_ip(request)
    inv = _load_valid_invitation(db, payload.token, current.id if current else None)

    if current is not None:
        if current.email != inv.email:
            raise ApiError(ErrorCode.INVITATION_EMAIL_MISMATCH, 403)
        user = db.get(User, current.id)
        assert user is not None  # noqa: S101
    else:
        if db.scalar(select(User.id).where(User.email == inv.email)) is not None:
            raise ApiError(ErrorCode.INVITATION_LOGIN_REQUIRED, 401)
        missing = [
            {"field": f, "message": "Ce champ est obligatoire."}
            for f, v in (("full_name", payload.full_name), ("password", payload.password))
            if not v
        ]
        if missing:
            raise ApiError(ErrorCode.VALIDATION_ERROR, 422, missing)
        user = User(
            email=inv.email,
            full_name=payload.full_name or "",
            password_hash=hash_password(payload.password or ""),
            is_active=True,
            is_platform_admin=False,
        )
        db.add(user)
        db.flush()
        set_tenant_context(db, user_id=user.id, org_id=inv.org_id)
        record(
            db,
            action="auth.signup",
            actor_user_id=user.id,
            ip_address=ip,
            details={"via": "invitation"},
        )
        open_session(db, response, user.id, ip, request.headers.get("user-agent"))

    membership = db.scalar(
        select(Membership).where(Membership.org_id == inv.org_id, Membership.user_id == user.id)
    )
    if membership is not None and membership.status == "active":
        raise ApiError(ErrorCode.ALREADY_MEMBER, 409)
    if membership is None:
        membership = Membership(org_id=inv.org_id, user_id=user.id, status="active")
        db.add(membership)
    else:
        membership.status = "active"
        db.execute(delete(MembershipRole).where(MembershipRole.membership_id == membership.id))
    db.flush()
    db.add(MembershipRole(membership_id=membership.id, role_key=inv.role_key, org_id=inv.org_id))
    inv.accepted_at = datetime.now(UTC)
    db.flush()
    record(
        db,
        action="invitation.accepted",
        org_id=inv.org_id,
        actor_user_id=user.id,
        target_type="invitation",
        target_id=inv.id,
        details={"role": inv.role_key},
        ip_address=ip,
    )
    return build_me(db, user)

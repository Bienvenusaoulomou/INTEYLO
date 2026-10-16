"""Organisation courante : paramètres, membres, rôles, invitations, audit."""

from datetime import UTC, datetime, timedelta
from typing import Annotated, NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.errors import ApiError, ErrorCode
from app.core.security import hash_token, new_token
from app.modules.audit.models import AuditEvent
from app.modules.audit.service import record, record_in_new_transaction
from app.modules.identity.deps import OrgContext, client_ip, load_roles, require_permission
from app.modules.identity.models import Role, RolePermission, User
from app.modules.identity.rbac import OWNER_ROLE
from app.modules.identity.schemas import InvitationCreateIn, OkOut, OrgUpdateIn, RolesUpdateIn
from app.modules.organizations.models import Invitation, Membership, MembershipRole
from app.modules.organizations.schemas import (
    AuditEventOut,
    AuditPageOut,
    InvitationCreatedOut,
    InvitationOut,
    MemberOut,
    MemberUser,
    OrganizationOut,
    RoleOut,
)

router = APIRouter(prefix="/v1/orgs/{org_id}", tags=["organisation"])


def _org_out(ctx: OrgContext) -> OrganizationOut:
    o = ctx.org
    return OrganizationOut(
        id=o.id,
        name=o.name,
        status=o.status,
        locale=o.locale,
        timezone=o.timezone,
        created_at=o.created_at,
    )


def _deny(
    ctx: OrgContext, request: Request, action: str, code: ErrorCode, **details: str
) -> NoReturn:
    record_in_new_transaction(
        action=action,
        outcome="denied",
        org_id=ctx.org.id,
        actor_user_id=ctx.user.id,
        details={"reason": code.value, **details},
        ip_address=client_ip(request),
    )
    raise ApiError(code, 403)


def _can_assign(ctx: OrgContext, role: Role) -> bool:
    return role.scope == "organization" and (ctx.is_owner or role.rank < ctx.max_rank)


def _active_owner_count(db: Session, org_id: UUID, exclude_membership: UUID) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(MembershipRole)
            .join(Membership, Membership.id == MembershipRole.membership_id)
            .where(
                MembershipRole.org_id == org_id,
                MembershipRole.role_key == OWNER_ROLE,
                Membership.status == "active",
                Membership.id != exclude_membership,
            )
        )
        or 0
    )


def _get_member(db: Session, ctx: OrgContext, membership_id: UUID) -> Membership:
    member = db.scalar(
        select(Membership).where(Membership.id == membership_id, Membership.org_id == ctx.org.id)
    )
    if member is None:
        raise ApiError(ErrorCode.MEMBER_NOT_FOUND, 404)
    return member


def _ensure_manageable(
    db: Session, ctx: OrgContext, request: Request, member: Membership, action: str
) -> list[Role]:
    if member.user_id == ctx.user.id:
        _deny(ctx, request, action, ErrorCode.CANNOT_MODIFY_SELF, membership_id=str(member.id))
    roles = load_roles(db, member.id)
    target_rank = max((r.rank for r in roles), default=0)
    if not ctx.is_owner and target_rank >= ctx.max_rank:
        _deny(ctx, request, action, ErrorCode.MEMBER_NOT_MANAGEABLE, membership_id=str(member.id))
    return roles


@router.get("", response_model=OrganizationOut)
def get_organization(
    ctx: OrgContext = Depends(require_permission("organizations.read")),
) -> OrganizationOut:
    return _org_out(ctx)


@router.patch("", response_model=OrganizationOut)
def update_organization(
    payload: OrgUpdateIn,
    request: Request,
    ctx: OrgContext = Depends(require_permission("organizations.manage")),
    db: Session = Depends(get_db),
) -> OrganizationOut:
    changes: dict[str, str] = {}
    if payload.name is not None and payload.name != ctx.org.name:
        changes["name"] = payload.name
        ctx.org.name = payload.name
    if payload.timezone is not None and payload.timezone != ctx.org.timezone:
        changes["timezone"] = payload.timezone
        ctx.org.timezone = payload.timezone
    if changes:
        db.flush()
        record(
            db,
            action="organization.updated",
            org_id=ctx.org.id,
            actor_user_id=ctx.user.id,
            target_type="organization",
            target_id=ctx.org.id,
            details={"changes": changes},
            ip_address=client_ip(request),
        )
    return _org_out(ctx)


@router.get("/roles", response_model=list[RoleOut])
def list_roles(
    ctx: OrgContext = Depends(require_permission("roles.read")), db: Session = Depends(get_db)
) -> list[RoleOut]:
    roles = db.scalars(select(Role).where(Role.scope == "organization").order_by(Role.rank.desc()))
    out = []
    for role in roles:
        perms = db.scalars(
            select(RolePermission.permission_key)
            .where(RolePermission.role_key == role.key)
            .order_by(RolePermission.permission_key)
        )
        out.append(
            RoleOut(
                key=role.key,
                rank=role.rank,
                permissions=list(perms),
                assignable=_can_assign(ctx, role),
            )
        )
    return out


@router.get("/members", response_model=list[MemberOut])
def list_members(
    ctx: OrgContext = Depends(require_permission("users.read")), db: Session = Depends(get_db)
) -> list[MemberOut]:
    rows = db.execute(
        select(Membership, User)
        .join(User, User.id == Membership.user_id)
        .where(Membership.org_id == ctx.org.id)
        .order_by(User.full_name)
    ).all()
    return [
        MemberOut(
            membership_id=m.id,
            user=MemberUser(id=u.id, email=u.email, full_name=u.full_name),
            status=m.status,
            roles=sorted(r.key for r in load_roles(db, m.id)),
            joined_at=m.created_at,
        )
        for m, u in rows
    ]


@router.put("/members/{membership_id}/roles", response_model=MemberOut)
def set_member_roles(
    membership_id: UUID,
    payload: RolesUpdateIn,
    request: Request,
    ctx: OrgContext = Depends(require_permission("roles.manage")),
    db: Session = Depends(get_db),
) -> MemberOut:
    member = _get_member(db, ctx, membership_id)
    current = _ensure_manageable(db, ctx, request, member, "member.roles_update")
    wanted_keys = sorted(set(payload.roles))
    wanted = list(db.scalars(select(Role).where(Role.key.in_(wanted_keys))))
    if len(wanted) != len(wanted_keys) or any(r.scope != "organization" for r in wanted):
        raise ApiError(ErrorCode.UNKNOWN_ROLE, 422)
    for role in wanted:
        if not _can_assign(ctx, role):
            _deny(ctx, request, "member.roles_update", ErrorCode.ROLE_NOT_ASSIGNABLE, role=role.key)
    current_keys = {r.key for r in current}
    if (
        OWNER_ROLE in current_keys
        and OWNER_ROLE not in wanted_keys
        and member.status == "active"
        and _active_owner_count(db, ctx.org.id, member.id) == 0
    ):
        raise ApiError(ErrorCode.LAST_OWNER, 409)

    db.execute(delete(MembershipRole).where(MembershipRole.membership_id == member.id))
    for key in wanted_keys:
        db.add(MembershipRole(membership_id=member.id, role_key=key, org_id=ctx.org.id))
    db.flush()
    record(
        db,
        action="member.roles_updated",
        org_id=ctx.org.id,
        actor_user_id=ctx.user.id,
        target_type="membership",
        target_id=member.id,
        details={"before": sorted(current_keys), "after": wanted_keys},
        ip_address=client_ip(request),
    )
    user = db.get(User, member.user_id)
    assert user is not None  # noqa: S101
    return MemberOut(
        membership_id=member.id,
        user=MemberUser(id=user.id, email=user.email, full_name=user.full_name),
        status=member.status,
        roles=wanted_keys,
        joined_at=member.created_at,
    )


def _set_member_status(
    membership_id: UUID, status: str, request: Request, ctx: OrgContext, db: Session
) -> OkOut:
    action = "member.disabled" if status == "disabled" else "member.enabled"
    member = _get_member(db, ctx, membership_id)
    roles = _ensure_manageable(db, ctx, request, member, action)
    if (
        status == "disabled"
        and any(r.key == OWNER_ROLE for r in roles)
        and _active_owner_count(db, ctx.org.id, member.id) == 0
    ):
        raise ApiError(ErrorCode.LAST_OWNER, 409)
    if member.status != status:
        member.status = status
        db.flush()
        record(
            db,
            action=action,
            org_id=ctx.org.id,
            actor_user_id=ctx.user.id,
            target_type="membership",
            target_id=member.id,
            ip_address=client_ip(request),
        )
    return OkOut()


@router.post("/members/{membership_id}/disable", response_model=OkOut)
def disable_member(
    membership_id: UUID,
    request: Request,
    ctx: OrgContext = Depends(require_permission("users.manage")),
    db: Session = Depends(get_db),
) -> OkOut:
    return _set_member_status(membership_id, "disabled", request, ctx, db)


@router.post("/members/{membership_id}/enable", response_model=OkOut)
def enable_member(
    membership_id: UUID,
    request: Request,
    ctx: OrgContext = Depends(require_permission("users.manage")),
    db: Session = Depends(get_db),
) -> OkOut:
    return _set_member_status(membership_id, "active", request, ctx, db)


def _invitation_status(inv: Invitation, now: datetime) -> str:
    if inv.accepted_at:
        return "accepted"
    if inv.revoked_at:
        return "revoked"
    if inv.expires_at <= now:
        return "expired"
    return "pending"


@router.get("/invitations", response_model=list[InvitationOut])
def list_invitations(
    ctx: OrgContext = Depends(require_permission("users.read")), db: Session = Depends(get_db)
) -> list[InvitationOut]:
    now = datetime.now(UTC)
    rows = db.execute(
        select(Invitation, User.full_name)
        .join(User, User.id == Invitation.invited_by, isouter=True)
        .where(Invitation.org_id == ctx.org.id)
        .order_by(Invitation.created_at.desc())
    ).all()
    return [
        InvitationOut(
            id=i.id,
            email=i.email,
            role=i.role_key,
            status=_invitation_status(i, now),
            created_at=i.created_at,
            expires_at=i.expires_at,
            invited_by_name=name,
        )
        for i, name in rows
    ]


@router.post("/invitations", response_model=InvitationCreatedOut, status_code=201)
def create_invitation(
    payload: InvitationCreateIn,
    request: Request,
    ctx: OrgContext = Depends(require_permission("users.invite")),
    db: Session = Depends(get_db),
) -> InvitationCreatedOut:
    role = db.get(Role, payload.role)
    if role is None or role.scope != "organization":
        raise ApiError(ErrorCode.UNKNOWN_ROLE, 422)
    if not _can_assign(ctx, role):
        _deny(ctx, request, "invitation.create", ErrorCode.ROLE_NOT_ASSIGNABLE, role=role.key)
    existing = db.scalar(
        select(Membership.status)
        .join(User, User.id == Membership.user_id)
        .where(Membership.org_id == ctx.org.id, User.email == payload.email)
    )
    if existing == "active":
        raise ApiError(ErrorCode.ALREADY_MEMBER, 409)
    now = datetime.now(UTC)
    pending = db.scalar(
        select(Invitation).where(
            Invitation.org_id == ctx.org.id,
            Invitation.email == payload.email,
            Invitation.accepted_at.is_(None),
            Invitation.revoked_at.is_(None),
        )
    )
    if pending is not None:
        if pending.expires_at > now:
            raise ApiError(ErrorCode.INVITATION_PENDING, 409)
        pending.revoked_at = now  # une invitation expirée est remplacée
        db.flush()

    settings = get_settings()
    token = new_token()
    inv = Invitation(
        org_id=ctx.org.id,
        email=payload.email,
        role_key=role.key,
        token_hash=hash_token(token),
        invited_by=ctx.user.id,
        expires_at=now + timedelta(hours=settings.invitation_ttl_hours),
    )
    db.add(inv)
    db.flush()
    record(
        db,
        action="invitation.created",
        org_id=ctx.org.id,
        actor_user_id=ctx.user.id,
        target_type="invitation",
        target_id=inv.id,
        details={"email": payload.email, "role": role.key},
        ip_address=client_ip(request),
    )
    return InvitationCreatedOut(
        id=inv.id,
        email=inv.email,
        role=inv.role_key,
        status="pending",
        created_at=inv.created_at,
        expires_at=inv.expires_at,
        invited_by_name=ctx.user.full_name,
        # Le jeton figure dans le fragment (#) : il n'est jamais envoyé au serveur web.
        accept_url=f"{settings.public_web_url.rstrip('/')}/invitation#{token}",
    )


@router.delete("/invitations/{invitation_id}", response_model=OkOut)
def revoke_invitation(
    invitation_id: UUID,
    request: Request,
    ctx: OrgContext = Depends(require_permission("users.invite")),
    db: Session = Depends(get_db),
) -> OkOut:
    inv = db.scalar(
        select(Invitation).where(Invitation.id == invitation_id, Invitation.org_id == ctx.org.id)
    )
    if inv is None:
        raise ApiError(ErrorCode.INVITATION_NOT_FOUND, 404)
    if inv.accepted_at is None and inv.revoked_at is None:
        inv.revoked_at = datetime.now(UTC)
        db.flush()
        record(
            db,
            action="invitation.revoked",
            org_id=ctx.org.id,
            actor_user_id=ctx.user.id,
            target_type="invitation",
            target_id=inv.id,
            ip_address=client_ip(request),
        )
    return OkOut()


@router.get("/audit", response_model=AuditPageOut)
def list_audit(
    ctx: OrgContext = Depends(require_permission("audit.read")),
    db: Session = Depends(get_db),
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0, le=100_000)] = 0,
) -> AuditPageOut:
    rows = db.execute(
        select(AuditEvent, User.email)
        .join(User, User.id == AuditEvent.actor_user_id, isouter=True)
        .where(AuditEvent.org_id == ctx.org.id)
        .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return AuditPageOut(
        items=[
            AuditEventOut(
                id=e.id,
                created_at=e.created_at,
                action=e.action,
                outcome=e.outcome,
                actor_email=email,
                target_type=e.target_type,
                target_id=e.target_id,
                details=e.details,
                ip_address=e.ip_address,
            )
            for e, email in rows
        ],
        limit=limit,
        offset=offset,
    )

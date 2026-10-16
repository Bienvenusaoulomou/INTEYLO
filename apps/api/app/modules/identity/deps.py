"""Dépendances d'authentification et d'autorisation.

Ordre des contrôles pour une route d'organisation : session valide → utilisateur actif →
membre actif de l'organisation (sinon 404, pour ne pas révéler son existence) →
organisation non suspendue → permission requise (sinon 403 + audit du refus).
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy import select, text, update
from sqlalchemy.orm import Session

from app.core.db import get_db, set_tenant_context
from app.core.errors import ApiError, ErrorCode
from app.core.security import hash_token
from app.modules.audit.service import record_in_new_transaction
from app.modules.identity.models import Role, RolePermission, User, UserSession
from app.modules.organizations.models import Membership, MembershipRole, Organization

SESSION_COOKIE = "inteylo_session"
_LAST_SEEN_REFRESH = timedelta(minutes=5)


@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    email: str
    full_name: str
    is_platform_admin: bool
    session_id: UUID


@dataclass(frozen=True)
class OrgContext:
    user: CurrentUser
    org: Organization
    membership: Membership
    role_keys: frozenset[str]
    permissions: frozenset[str]
    max_rank: int

    @property
    def is_owner(self) -> bool:
        return "org_owner" in self.role_keys


def client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _resolve_session(request: Request, db: Session) -> CurrentUser | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    row = db.execute(
        text("select * from session_lookup(:h)"), {"h": hash_token(token)}
    ).one_or_none()
    now = datetime.now(UTC)
    if row is None or row.revoked_at is not None or row.expires_at <= now:
        return None
    set_tenant_context(db, user_id=row.user_id)
    user = db.get(User, row.user_id)
    if user is None or not user.is_active:
        return None
    if now - row.last_seen_at > _LAST_SEEN_REFRESH:
        db.execute(
            update(UserSession).where(UserSession.id == row.session_id).values(last_seen_at=now)
        )
    set_tenant_context(db, user_id=user.id, platform_admin=user.is_platform_admin)
    return CurrentUser(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_platform_admin=user.is_platform_admin,
        session_id=row.session_id,
    )


def get_optional_user(request: Request, db: Session = Depends(get_db)) -> CurrentUser | None:
    return _resolve_session(request, db)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> CurrentUser:
    user = _resolve_session(request, db)
    if user is None:
        raise ApiError(ErrorCode.AUTHENTICATION_REQUIRED, 401)
    return user


def load_roles(db: Session, membership_id: UUID) -> list[Role]:
    return list(
        db.scalars(
            select(Role)
            .join(MembershipRole, MembershipRole.role_key == Role.key)
            .where(MembershipRole.membership_id == membership_id)
        )
    )


def load_permissions(db: Session, role_keys: frozenset[str]) -> frozenset[str]:
    if not role_keys:
        return frozenset()
    return frozenset(
        db.scalars(
            select(RolePermission.permission_key).where(RolePermission.role_key.in_(role_keys))
        )
    )


def get_org_context(
    org_id: UUID,
    request: Request,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgContext:
    # Le statut de super-administrateur ne donne aucun accès aux données d'une organisation.
    set_tenant_context(db, user_id=user.id, org_id=org_id, platform_admin=False)
    membership = db.scalar(
        select(Membership).where(
            Membership.org_id == org_id,
            Membership.user_id == user.id,
            Membership.status == "active",
        )
    )
    if membership is None:
        record_in_new_transaction(
            action="organization.access",
            outcome="denied",
            org_id=None,
            actor_user_id=user.id,
            details={"reason": "not_a_member", "requested_org_id": str(org_id)},
            ip_address=client_ip(request),
        )
        raise ApiError(ErrorCode.ORGANIZATION_NOT_FOUND, 404)
    org = db.get(Organization, org_id)
    if org is None:
        raise ApiError(ErrorCode.ORGANIZATION_NOT_FOUND, 404)
    if org.status != "active":
        raise ApiError(ErrorCode.ORGANIZATION_SUSPENDED, 403)
    roles = load_roles(db, membership.id)
    role_keys = frozenset(r.key for r in roles)
    return OrgContext(
        user=user,
        org=org,
        membership=membership,
        role_keys=role_keys,
        permissions=load_permissions(db, role_keys),
        max_rank=max((r.rank for r in roles), default=0),
    )


def require_permission(permission: str) -> Callable[..., OrgContext]:
    def dependency(request: Request, ctx: OrgContext = Depends(get_org_context)) -> OrgContext:
        if permission not in ctx.permissions:
            record_in_new_transaction(
                action="permission.check",
                outcome="denied",
                org_id=ctx.org.id,
                actor_user_id=ctx.user.id,
                details={
                    "permission": permission,
                    "method": request.method,
                    "path": request.url.path,
                },
                ip_address=client_ip(request),
            )
            raise ApiError(ErrorCode.PERMISSION_DENIED, 403)
        return ctx

    return dependency


def require_platform_admin(
    request: Request,
    user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if not user.is_platform_admin:
        record_in_new_transaction(
            action="platform.access",
            outcome="denied",
            org_id=None,
            actor_user_id=user.id,
            details={"path": request.url.path},
            ip_address=client_ip(request),
        )
        raise ApiError(ErrorCode.PERMISSION_DENIED, 403)
    return user

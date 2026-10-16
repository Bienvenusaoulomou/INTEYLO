"""Services d'identité : sessions et vue « moi »."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_token, new_token
from app.modules.identity.deps import SESSION_COOKIE, load_permissions, load_roles
from app.modules.identity.models import User, UserSession
from app.modules.identity.schemas import MembershipOut, MeOut, OrganizationSummary, UserOut
from app.modules.organizations.models import Membership, Organization


def open_session(
    db: Session, response: Response, user_id: UUID, ip: str | None, user_agent: str | None
) -> UserSession:
    settings = get_settings()
    token = new_token()
    now = datetime.now(UTC)
    session = UserSession(
        user_id=user_id,
        token_hash=hash_token(token),
        expires_at=now + timedelta(hours=settings.session_ttl_hours),
        last_seen_at=now,
        ip_address=ip,
        user_agent=(user_agent or "")[:300] or None,
    )
    db.add(session)
    db.flush()
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=settings.session_ttl_hours * 3600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    return session


def clear_session_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        SESSION_COOKIE, path="/", httponly=True, secure=settings.cookie_secure, samesite="lax"
    )


def build_me(db: Session, user: User) -> MeOut:
    rows = db.execute(
        select(Membership, Organization)
        .join(Organization, Organization.id == Membership.org_id)
        .where(Membership.user_id == user.id, Membership.status == "active")
        .order_by(Organization.name)
    ).all()
    memberships: list[MembershipOut] = []
    for membership, org in rows:
        role_keys = frozenset(r.key for r in load_roles(db, membership.id))
        memberships.append(
            MembershipOut(
                organization=OrganizationSummary(id=org.id, name=org.name, status=org.status),
                roles=sorted(role_keys),
                permissions=sorted(load_permissions(db, role_keys)),
            )
        )
    return MeOut(
        user=UserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_platform_admin=user.is_platform_admin,
        ),
        memberships=memberships,
    )

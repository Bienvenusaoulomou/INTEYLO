from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db, set_tenant_context
from app.core.errors import ApiError, ErrorCode
from app.core.rate_limit import SlidingWindowLimiter
from app.core.security import hash_password, verify_password
from app.modules.audit.service import record, record_in_new_transaction
from app.modules.identity.deps import CurrentUser, client_ip, get_current_user
from app.modules.identity.models import User, UserSession
from app.modules.identity.rbac import OWNER_ROLE
from app.modules.identity.schemas import (
    LoginIn,
    MeOut,
    OkOut,
    RevokedOut,
    SessionOut,
    SignupIn,
)
from app.modules.identity.service import build_me, clear_session_cookie, open_session
from app.modules.organizations.models import Membership, MembershipRole, Organization

router = APIRouter(prefix="/v1/auth", tags=["authentification"])

_settings = get_settings()
login_limiter = SlidingWindowLimiter(_settings.login_max_attempts, _settings.login_window_seconds)
signup_limiter = SlidingWindowLimiter(_settings.login_max_attempts, _settings.login_window_seconds)


@router.post("/signup", response_model=MeOut, status_code=201)
def signup(
    payload: SignupIn, request: Request, response: Response, db: Session = Depends(get_db)
) -> MeOut:
    ip = client_ip(request)
    key = f"signup:{ip}"
    if signup_limiter.is_blocked(key):
        raise ApiError(ErrorCode.TOO_MANY_ATTEMPTS, 429)
    signup_limiter.hit(key)
    if db.scalar(select(User.id).where(User.email == payload.email)) is not None:
        raise ApiError(ErrorCode.EMAIL_ALREADY_USED, 409)

    user_id, org_id = uuid4(), uuid4()
    set_tenant_context(db, user_id=user_id, org_id=org_id)
    user = User(
        id=user_id,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        is_active=True,
        is_platform_admin=False,
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError as exc:
        raise ApiError(ErrorCode.EMAIL_ALREADY_USED, 409) from exc
    db.add(Organization(id=org_id, name=payload.organization_name, timezone=payload.timezone))
    db.flush()
    membership = Membership(org_id=org_id, user_id=user_id, status="active")
    db.add(membership)
    db.flush()
    db.add(MembershipRole(membership_id=membership.id, role_key=OWNER_ROLE, org_id=org_id))
    open_session(db, response, user_id, ip, request.headers.get("user-agent"))
    record(db, action="auth.signup", org_id=None, actor_user_id=user_id, ip_address=ip)
    record(
        db,
        action="organization.created",
        org_id=org_id,
        actor_user_id=user_id,
        target_type="organization",
        target_id=org_id,
        ip_address=ip,
    )
    return build_me(db, user)


@router.post("/login", response_model=MeOut)
def login(
    payload: LoginIn, request: Request, response: Response, db: Session = Depends(get_db)
) -> MeOut:
    ip = client_ip(request)
    key = f"login:{ip}:{payload.email}"
    if login_limiter.is_blocked(key):
        record_in_new_transaction(
            action="auth.login",
            outcome="denied",
            org_id=None,
            actor_user_id=None,
            details={"reason": "rate_limited", "email": payload.email},
            ip_address=ip,
        )
        raise ApiError(ErrorCode.TOO_MANY_ATTEMPTS, 429)

    user = db.scalar(select(User).where(User.email == payload.email))
    valid = verify_password(user.password_hash if user else None, payload.password)
    if user is None or not valid or not user.is_active:
        login_limiter.hit(key)
        record_in_new_transaction(
            action="auth.login",
            outcome="failure",
            org_id=None,
            actor_user_id=None,
            details={"reason": "invalid_credentials", "email": payload.email},
            ip_address=ip,
        )
        raise ApiError(ErrorCode.INVALID_CREDENTIALS, 401)

    login_limiter.reset(key)
    set_tenant_context(db, user_id=user.id)
    open_session(db, response, user.id, ip, request.headers.get("user-agent"))
    record(db, action="auth.login", actor_user_id=user.id, ip_address=ip)
    return build_me(db, user)


@router.post("/logout", response_model=OkOut)
def logout(
    request: Request,
    response: Response,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OkOut:
    db.execute(
        update(UserSession)
        .where(UserSession.id == user.session_id)
        .values(revoked_at=datetime.now(UTC))
    )
    record(db, action="auth.logout", actor_user_id=user.id, ip_address=client_ip(request))
    clear_session_cookie(response)
    return OkOut()


@router.get("/me", response_model=MeOut)
def me(user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> MeOut:
    db_user = db.get(User, user.id)
    assert db_user is not None  # noqa: S101 - garanti par get_current_user
    return build_me(db, db_user)


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(
    user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[SessionOut]:
    now = datetime.now(UTC)
    sessions = db.scalars(
        select(UserSession)
        .where(
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > now,
        )
        .order_by(UserSession.last_seen_at.desc())
    )
    return [
        SessionOut(
            id=s.id,
            created_at=s.created_at,
            last_seen_at=s.last_seen_at,
            expires_at=s.expires_at,
            ip_address=s.ip_address,
            user_agent=s.user_agent,
            current=s.id == user.session_id,
        )
        for s in sessions
    ]


@router.delete("/sessions/{session_id}", response_model=OkOut)
def revoke_session(
    session_id: UUID,
    request: Request,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OkOut:
    result = db.execute(
        update(UserSession)
        .where(
            UserSession.id == session_id,
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(UTC))
    )
    if result.rowcount == 0:  # type: ignore[attr-defined]
        raise ApiError(ErrorCode.SESSION_NOT_FOUND, 404)
    record(
        db,
        action="auth.session_revoked",
        actor_user_id=user.id,
        target_type="session",
        target_id=session_id,
        ip_address=client_ip(request),
    )
    return OkOut()


@router.post("/sessions/revoke-others", response_model=RevokedOut)
def revoke_other_sessions(
    request: Request,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RevokedOut:
    result = db.execute(
        update(UserSession)
        .where(
            UserSession.user_id == user.id,
            UserSession.id != user.session_id,
            UserSession.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(UTC))
    )
    count = int(result.rowcount)  # type: ignore[attr-defined]
    record(
        db,
        action="auth.other_sessions_revoked",
        actor_user_id=user.id,
        details={"count": count},
        ip_address=client_ip(request),
    )
    return RevokedOut(revoked=count)

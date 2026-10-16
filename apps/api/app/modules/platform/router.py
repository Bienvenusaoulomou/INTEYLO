"""Administration de la plateforme (super-administrateur).

Limites volontaires : le super-administrateur voit la liste des organisations et peut les
suspendre ou les réactiver. Il n'a aucun accès aux données métier, aux membres ou à
l'audit interne d'une organisation (accès « bris de glace » prévu au backlog, avec
justification et double validation).
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db, set_tenant_context
from app.core.errors import ApiError, ErrorCode
from app.modules.audit.service import record
from app.modules.identity.deps import CurrentUser, client_ip, require_platform_admin
from app.modules.identity.schemas import OkOut
from app.modules.organizations.models import Membership, Organization

router = APIRouter(prefix="/v1/platform", tags=["plateforme"])
_STATUS_ACTIONS = {
    "suspended": "platform.organization_suspended",
    "active": "platform.organization_reactivated",
}


class PlatformOrgOut(BaseModel):
    id: UUID
    name: str
    status: str
    created_at: datetime
    active_members: int


@router.get("/organizations", response_model=list[PlatformOrgOut])
def list_organizations(
    admin: CurrentUser = Depends(require_platform_admin), db: Session = Depends(get_db)
) -> list[PlatformOrgOut]:
    set_tenant_context(db, user_id=admin.id, platform_admin=True)
    counts = (
        select(Membership.org_id, func.count().label("n"))
        .where(Membership.status == "active")
        .group_by(Membership.org_id)
        .subquery()
    )
    rows = db.execute(
        select(Organization, func.coalesce(counts.c.n, 0))
        .join(counts, counts.c.org_id == Organization.id, isouter=True)
        .order_by(Organization.created_at.desc())
    ).all()
    return [
        PlatformOrgOut(
            id=o.id, name=o.name, status=o.status, created_at=o.created_at, active_members=int(n)
        )
        for o, n in rows
    ]


def _set_status(
    org_id: UUID, status: str, admin: CurrentUser, request: Request, db: Session
) -> OkOut:
    set_tenant_context(db, user_id=admin.id, org_id=org_id, platform_admin=True)
    org = db.get(Organization, org_id)
    if org is None:
        raise ApiError(ErrorCode.ORGANIZATION_NOT_FOUND, 404)
    if org.status != status:
        org.status = status
        db.flush()
        record(
            db,
            action=_STATUS_ACTIONS[status],
            org_id=org.id,
            actor_user_id=admin.id,
            target_type="organization",
            target_id=org.id,
            ip_address=client_ip(request),
        )
    return OkOut()


@router.post("/organizations/{org_id}/suspend", response_model=OkOut)
def suspend_organization(
    org_id: UUID,
    request: Request,
    admin: CurrentUser = Depends(require_platform_admin),
    db: Session = Depends(get_db),
) -> OkOut:
    return _set_status(org_id, "suspended", admin, request, db)


@router.post("/organizations/{org_id}/reactivate", response_model=OkOut)
def reactivate_organization(
    org_id: UUID,
    request: Request,
    admin: CurrentUser = Depends(require_platform_admin),
    db: Session = Depends(get_db),
) -> OkOut:
    return _set_status(org_id, "active", admin, request, db)

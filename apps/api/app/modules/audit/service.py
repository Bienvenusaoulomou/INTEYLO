"""Écriture du journal d'audit.

Les refus d'autorisation sont journalisés dans une transaction séparée : la transaction
de la requête est annulée par l'erreur, mais la trace du refus doit être conservée.
"""

import logging
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.core.db import get_session_factory, set_tenant_context
from app.modules.audit.models import AuditEvent

logger = logging.getLogger("inteylo.audit")

# Clés jamais écrites dans l'audit, même si un appelant les transmet par erreur.
_FORBIDDEN_DETAIL_KEYS = {"password", "token", "token_hash", "secret", "cookie"}


def _clean(details: dict[str, Any] | None) -> dict[str, Any]:
    return {k: v for k, v in (details or {}).items() if k.lower() not in _FORBIDDEN_DETAIL_KEYS}


def record(
    db: Session,
    *,
    action: str,
    outcome: str = "success",
    org_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    target_type: str | None = None,
    target_id: str | UUID | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> None:
    # Insertion sans RETURNING : le rôle applicatif peut écrire un événement qu'il n'a pas
    # le droit de relire (événements hors organisation, réservés à la plateforme).
    db.flush()
    db.execute(
        insert(AuditEvent).values(
            id=uuid4(),
            org_id=org_id,
            actor_user_id=actor_user_id,
            action=action,
            outcome=outcome,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            details=_clean(details),
            ip_address=ip_address,
        )
    )


def record_in_new_transaction(
    *,
    action: str,
    outcome: str,
    org_id: UUID | None,
    actor_user_id: UUID | None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
    target_type: str | None = None,
    target_id: str | UUID | None = None,
) -> None:
    try:
        with get_session_factory()() as session, session.begin():
            set_tenant_context(session, user_id=actor_user_id, org_id=org_id)
            record(
                session,
                action=action,
                outcome=outcome,
                org_id=org_id,
                actor_user_id=actor_user_id,
                details=details,
                ip_address=ip_address,
                target_type=target_type,
                target_id=target_id,
            )
    except Exception:  # l'échec d'audit ne doit pas masquer l'erreur d'origine
        logger.exception("audit write failed", extra={"action": action})

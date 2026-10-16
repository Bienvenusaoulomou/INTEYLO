"""Accès base de données et contexte de locataire (RLS).

Chaque requête HTTP s'exécute dans une transaction unique. Le contexte (utilisateur,
organisation, mode plateforme) est posé avec ``set_config(..., is_local => true)`` :
il disparaît à la fin de la transaction et ne fuit jamais vers une autre requête
réutilisant la même connexion du pool.
"""

from collections.abc import Iterator
from functools import lru_cache
from uuid import UUID

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True, pool_size=10)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(get_engine(), expire_on_commit=False, autoflush=True)


def get_db() -> Iterator[Session]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()


def set_tenant_context(
    db: Session,
    *,
    user_id: UUID | None = None,
    org_id: UUID | None = None,
    platform_admin: bool = False,
) -> None:
    db.execute(
        text(
            "select set_config('app.current_user_id', :user_id, true),"
            " set_config('app.current_org_id', :org_id, true),"
            " set_config('app.platform_admin', :platform, true)"
        ),
        {
            "user_id": str(user_id) if user_id else "",
            "org_id": str(org_id) if org_id else "",
            "platform": "on" if platform_admin else "off",
        },
    )


def check_database_role(db: Session) -> list[str]:
    """Retourne la liste des problèmes de configuration du rôle applicatif.

    L'API doit se connecter avec un rôle qui n'est ni superutilisateur, ni BYPASSRLS,
    ni propriétaire des tables : sinon la RLS ne s'applique pas.
    """
    problems: list[str] = []
    row = db.execute(
        text("select rolsuper, rolbypassrls from pg_roles where rolname = current_user")
    ).one()
    if row.rolsuper:
        problems.append("database role is superuser")
    if row.rolbypassrls:
        problems.append("database role has BYPASSRLS")
    owned = db.execute(
        text(
            "select count(*) from pg_tables where schemaname = 'public'"
            " and tableowner = current_user"
        )
    ).scalar_one()
    if owned:
        problems.append("database role owns application tables")
    return problems

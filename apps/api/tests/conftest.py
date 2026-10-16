"""Fixtures de test : vraie base PostgreSQL, migrations réelles, rôle applicatif soumis à la RLS.

Variable requise : INTEYLO_TEST_ADMIN_URL (superutilisateur), par exemple
postgresql+psycopg://postgres@127.0.0.1:5433/postgres
"""

import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

API_DIR = Path(__file__).resolve().parents[1]
ADMIN_URL = os.environ.get(
    "INTEYLO_TEST_ADMIN_URL", "postgresql+psycopg://postgres@127.0.0.1:5433/postgres"
)
DB_NAME = "inteylo_test"
OWNER, OWNER_PW = "inteylo_owner_test", "owner-test-password"
APP, APP_PW = "inteylo_app_test", "app-test-password"


def _url(user: str, password: str, database: str) -> str:
    base = make_url(ADMIN_URL)
    return base.set(username=user, password=password, database=database).render_as_string(
        hide_password=False
    )


OWNER_URL = _url(OWNER, OWNER_PW, DB_NAME)
APP_URL = _url(APP, APP_PW, DB_NAME)

os.environ.update(
    {
        "INTEYLO_ENVIRONMENT": "test",
        "INTEYLO_DATABASE_URL": APP_URL,
        "INTEYLO_COOKIE_SECURE": "false",
        "INTEYLO_PUBLIC_WEB_URL": "http://localhost:3000",
        "INTEYLO_LOG_LEVEL": "WARNING",
    }
)


def _bootstrap_database() -> None:
    admin = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    with admin.connect() as c:
        c.execute(text(f"DROP DATABASE IF EXISTS {DB_NAME} WITH (FORCE)"))
        for role, pw in ((OWNER, OWNER_PW), (APP, APP_PW)):
            exists = c.execute(text("select 1 from pg_roles where rolname=:r"), {"r": role}).first()
            if not exists:
                c.execute(text(f"CREATE ROLE {role} LOGIN PASSWORD '{pw}'"))
        c.execute(text(f"CREATE DATABASE {DB_NAME} OWNER {OWNER}"))
    admin.dispose()
    env = {**os.environ, "INTEYLO_MIGRATION_DATABASE_URL": OWNER_URL, "INTEYLO_APP_DB_ROLE": APP}
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"], cwd=API_DIR, env=env, check=True
    )


_bootstrap_database()

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.modules.identity.router import login_limiter, signup_limiter  # noqa: E402

owner_engine = create_engine(OWNER_URL)
_TABLES = "audit_events, invitations, membership_roles, memberships, sessions, organizations, users"


@pytest.fixture(autouse=True)
def _clean_database() -> Iterator[None]:
    yield
    with owner_engine.begin() as c:
        c.execute(text("ALTER TABLE audit_events DISABLE TRIGGER trg_audit_events_immutable"))
        c.execute(text(f"TRUNCATE {_TABLES} CASCADE"))
        c.execute(text("ALTER TABLE audit_events ENABLE TRIGGER trg_audit_events_immutable"))
    login_limiter.reset()
    signup_limiter.reset()


class Api:
    """Client HTTP d'un navigateur : cookies propres + en-tête anti-CSRF."""

    def __init__(self) -> None:
        self.client = TestClient(app)
        self.client.headers["x-inteylo-client"] = "web"

    def __getattr__(self, name: str) -> Any:
        return getattr(self.client, name)


@pytest.fixture
def make_client() -> Any:
    return Api


def signup(
    api: Api, email: str, org: str = "Organisation A", name: str = "Personne Test"
) -> dict[str, Any]:
    r = api.post(
        "/v1/auth/signup",
        json={
            "email": email,
            "password": "motdepasse-solide-123",
            "full_name": name,
            "organization_name": org,
            "timezone": "Africa/Tunis",
        },
    )
    assert r.status_code == 201, r.text
    data: dict[str, Any] = r.json()
    return data


def org_id_of(me: dict[str, Any]) -> str:
    return str(me["memberships"][0]["organization"]["id"])


def invite_and_join(owner: Api, org_id: str, email: str, role: str) -> tuple[Api, dict[str, Any]]:
    r = owner.post(f"/v1/orgs/{org_id}/invitations", json={"email": email, "role": role})
    assert r.status_code == 201, r.text
    token = r.json()["accept_url"].split("#", 1)[1]
    member = Api()
    r = member.post(
        "/v1/invitations/accept",
        json={"token": token, "full_name": "Invité Test", "password": "motdepasse-solide-456"},
    )
    assert r.status_code == 200, r.text
    return member, r.json()


def membership_id(owner: Api, org_id: str, email: str) -> str:
    members = owner.get(f"/v1/orgs/{org_id}/members").json()
    return next(m["membership_id"] for m in members if m["user"]["email"] == email)


def audit_actions(org_id: str) -> list[tuple[str, str]]:
    with owner_engine.connect() as c:
        rows = c.execute(
            text("select action, outcome from audit_events where org_id = :o order by created_at"),
            {"o": org_id},
        ).all()
    return [(r.action, r.outcome) for r in rows]

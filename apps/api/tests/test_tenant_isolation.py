"""Isolation entre organisations : couche applicative ET base de données (RLS)."""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from tests.conftest import APP_URL, Api, audit_actions, membership_id, org_id_of, signup

app_engine = create_engine(APP_URL)


@pytest.fixture
def two_orgs() -> tuple[Api, str, Api, str]:
    a, b = Api(), Api()
    org_a = org_id_of(signup(a, "a@exemple.fr", org="Organisation A"))
    org_b = org_id_of(signup(b, "b@exemple.fr", org="Organisation B"))
    return a, org_a, b, org_b


@pytest.mark.parametrize(
    ("method", "suffix"),
    [
        ("get", ""),
        ("get", "/members"),
        ("get", "/invitations"),
        ("get", "/audit"),
        ("get", "/roles"),
        ("patch", ""),
        ("post", "/invitations"),
    ],
)
def test_foreign_org_endpoints_return_404(two_orgs, method: str, suffix: str) -> None:  # type: ignore[no-untyped-def]
    _, org_a, b, _ = two_orgs
    kwargs = {"json": {"email": "x@exemple.fr", "role": "viewer"}} if method == "post" else {}
    if method == "patch":
        kwargs = {"json": {"name": "Piratage"}}
    r = getattr(b, method)(f"/v1/orgs/{org_a}{suffix}", **kwargs)
    assert r.status_code == 404
    assert r.json()["error"]["message"] == "Organisation introuvable."


def test_foreign_access_attempt_is_audited(two_orgs) -> None:  # type: ignore[no-untyped-def]
    from tests.conftest import owner_engine

    _, org_a, b, _ = two_orgs
    b.get(f"/v1/orgs/{org_a}/members")
    with owner_engine.connect() as c:
        row = c.execute(
            text("select outcome, details from audit_events where action='organization.access'")
        ).one()
    assert row.outcome == "denied"
    assert row.details["requested_org_id"] == org_a


def test_cannot_target_foreign_membership_through_own_org(two_orgs) -> None:  # type: ignore[no-untyped-def]
    a, org_a, b, org_b = two_orgs
    foreign_membership = membership_id(a, org_a, "a@exemple.fr")
    r = b.put(f"/v1/orgs/{org_b}/members/{foreign_membership}/roles", json={"roles": ["viewer"]})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "member_not_found"
    assert a.get(f"/v1/orgs/{org_a}/members").json()[0]["roles"] == ["org_owner"]


def test_me_lists_only_own_memberships(two_orgs) -> None:  # type: ignore[no-untyped-def]
    a, org_a, _, _ = two_orgs
    memberships = a.get("/v1/auth/me").json()["memberships"]
    assert [m["organization"]["id"] for m in memberships] == [org_a]


def _as_app(org_id: str | None, user_id: str | None = None):  # type: ignore[no-untyped-def]
    conn = app_engine.connect()
    trans = conn.begin()
    conn.execute(
        text(
            "select set_config('app.current_org_id', :o, true),"
            " set_config('app.current_user_id', :u, true)"
        ),
        {"o": org_id or "", "u": user_id or ""},
    )
    return conn, trans


def test_rls_hides_other_tenants_rows_even_without_where_clause(two_orgs) -> None:  # type: ignore[no-untyped-def]
    _, org_a, _, org_b = two_orgs
    conn, trans = _as_app(org_b)
    try:
        orgs = conn.execute(text("select id from organizations")).scalars().all()
        members = conn.execute(text("select org_id from memberships")).scalars().all()
        audit = conn.execute(text("select org_id from audit_events")).scalars().all()
    finally:
        trans.rollback()
        conn.close()
    assert [str(o) for o in orgs] == [org_b]
    assert {str(m) for m in members} == {org_b}
    assert org_a not in {str(x) for x in audit}


def test_rls_without_context_returns_nothing(two_orgs) -> None:  # type: ignore[no-untyped-def]
    conn, trans = _as_app(None)
    try:
        for table in (
            "organizations",
            "memberships",
            "membership_roles",
            "invitations",
            "audit_events",
            "sessions",
        ):
            assert conn.execute(text(f"select count(*) from {table}")).scalar_one() == 0  # noqa: S608
    finally:
        trans.rollback()
        conn.close()


def test_rls_blocks_cross_tenant_writes(two_orgs) -> None:  # type: ignore[no-untyped-def]
    _, org_a, _, org_b = two_orgs
    conn, trans = _as_app(org_b)
    try:
        with pytest.raises(DBAPIError, match="row-level security"):
            conn.execute(
                text("insert into memberships (org_id, user_id) select :a, id from users limit 1"),
                {"a": org_a},
            )
    finally:
        trans.rollback()
        conn.close()
    conn, trans = _as_app(org_b)
    try:
        updated = conn.execute(
            text("update organizations set name = 'pirate' where id = :a"), {"a": org_a}
        ).rowcount
    finally:
        trans.rollback()
        conn.close()
    assert updated == 0


def test_app_role_cannot_bypass_rls() -> None:
    with app_engine.connect() as c:
        row = c.execute(
            text("select rolsuper, rolbypassrls from pg_roles where rolname = current_user")
        ).one()
    assert (row.rolsuper, row.rolbypassrls) == (False, False)


def test_audit_trail_stays_in_its_tenant(two_orgs) -> None:  # type: ignore[no-untyped-def]
    a, org_a, _, org_b = two_orgs
    a.patch(f"/v1/orgs/{org_a}", json={"name": "Nouveau nom A"})
    assert ("organization.updated", "success") in audit_actions(org_a)
    assert ("organization.updated", "success") not in audit_actions(org_b)

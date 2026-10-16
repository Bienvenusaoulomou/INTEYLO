"""Autorisations : refus par défaut, élévation de privilèges, rangs, révocation."""

from sqlalchemy import create_engine, text

from app.modules.identity.rbac import ORG_ROLE_RANKS, PLATFORM_ROLE_RANKS, ROLE_PERMISSIONS
from tests.conftest import (
    APP_URL,
    Api,
    audit_actions,
    invite_and_join,
    membership_id,
    org_id_of,
    signup,
)


def _org_with_owner() -> tuple[Api, str]:
    owner = Api()
    return owner, org_id_of(signup(owner, "proprio@exemple.fr"))


def test_rbac_seed_matches_reference() -> None:
    engine = create_engine(APP_URL)
    with engine.connect() as c:
        roles = dict(c.execute(text("select key, rank from roles")).all())
        pairs = c.execute(text("select role_key, permission_key from role_permissions")).all()
    assert roles == {**ORG_ROLE_RANKS, **PLATFORM_ROLE_RANKS}
    seeded: dict[str, set[str]] = {}
    for role, perm in pairs:
        seeded.setdefault(role, set()).add(perm)
    assert seeded == {k: set(v) for k, v in ROLE_PERMISSIONS.items()}


def test_viewer_cannot_invite_and_refusal_is_audited() -> None:
    owner, org = _org_with_owner()
    viewer, _ = invite_and_join(owner, org, "lecteur@exemple.fr", "viewer")
    r = viewer.post(f"/v1/orgs/{org}/invitations", json={"email": "x@exemple.fr", "role": "viewer"})
    assert r.status_code == 403
    assert (
        r.json()["error"]["message"]
        == "Vous n'avez pas l'autorisation d'effectuer cette opération."
    )
    assert ("permission.check", "denied") in audit_actions(org)


def test_viewer_and_analyst_cannot_read_audit_or_manage_roles() -> None:
    owner, org = _org_with_owner()
    viewer, _ = invite_and_join(owner, org, "lecteur@exemple.fr", "viewer")
    analyst, _ = invite_and_join(owner, org, "analyste@exemple.fr", "analyst")
    target = membership_id(owner, org, "lecteur@exemple.fr")
    for api in (viewer, analyst):
        assert api.get(f"/v1/orgs/{org}/audit").status_code == 403
        assert (
            api.put(
                f"/v1/orgs/{org}/members/{target}/roles", json={"roles": ["org_admin"]}
            ).status_code
            == 403
        )
    assert viewer.get(f"/v1/orgs/{org}/members").status_code == 403
    assert analyst.get(f"/v1/orgs/{org}/members").status_code == 200


def test_admin_cannot_grant_admin_or_owner() -> None:
    owner, org = _org_with_owner()
    admin, _ = invite_and_join(owner, org, "admin@exemple.fr", "org_admin")
    for role in ("org_admin", "org_owner"):
        r = admin.post(
            f"/v1/orgs/{org}/invitations", json={"email": f"{role}@exemple.fr", "role": role}
        )
        assert r.status_code == 403
        assert r.json()["error"]["code"] == "role_not_assignable"
    assert (
        admin.post(
            f"/v1/orgs/{org}/invitations", json={"email": "ok@exemple.fr", "role": "analyst"}
        ).status_code
        == 201
    )
    invite_and_join(owner, org, "lecteur@exemple.fr", "viewer")
    target = membership_id(owner, org, "lecteur@exemple.fr")
    r = admin.put(f"/v1/orgs/{org}/members/{target}/roles", json={"roles": ["org_admin"]})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "role_not_assignable"
    r = admin.put(f"/v1/orgs/{org}/members/{target}/roles", json={"roles": ["operator"]})
    assert r.status_code == 200
    assert r.json()["roles"] == ["operator"]


def test_admin_cannot_touch_owner_or_peer_admin() -> None:
    owner, org = _org_with_owner()
    admin, _ = invite_and_join(owner, org, "admin@exemple.fr", "org_admin")
    invite_and_join(owner, org, "admin2@exemple.fr", "org_admin")
    for email in ("proprio@exemple.fr", "admin2@exemple.fr"):
        target = membership_id(owner, org, email)
        r = admin.put(f"/v1/orgs/{org}/members/{target}/roles", json={"roles": ["viewer"]})
        assert r.status_code == 403
        assert r.json()["error"]["code"] == "member_not_manageable"
        assert admin.post(f"/v1/orgs/{org}/members/{target}/disable").status_code == 403


def test_nobody_can_modify_their_own_roles() -> None:
    owner, org = _org_with_owner()
    me = membership_id(owner, org, "proprio@exemple.fr")
    r = owner.put(f"/v1/orgs/{org}/members/{me}/roles", json={"roles": ["viewer"]})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "cannot_modify_self"
    assert owner.post(f"/v1/orgs/{org}/members/{me}/disable").status_code == 403


def test_platform_role_cannot_be_assigned_in_an_org() -> None:
    owner, org = _org_with_owner()
    invite_and_join(owner, org, "lecteur@exemple.fr", "viewer")
    target = membership_id(owner, org, "lecteur@exemple.fr")
    r = owner.put(
        f"/v1/orgs/{org}/members/{target}/roles", json={"roles": ["platform_super_admin"]}
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "unknown_role"
    r = owner.post(
        f"/v1/orgs/{org}/invitations",
        json={"email": "z@exemple.fr", "role": "platform_super_admin"},
    )
    assert r.status_code == 422


def test_owner_can_promote_and_new_rights_apply_immediately() -> None:
    owner, org = _org_with_owner()
    member, _ = invite_and_join(owner, org, "lecteur@exemple.fr", "viewer")
    assert member.get(f"/v1/orgs/{org}/audit").status_code == 403
    target = membership_id(owner, org, "lecteur@exemple.fr")
    assert (
        owner.put(
            f"/v1/orgs/{org}/members/{target}/roles", json={"roles": ["org_admin"]}
        ).status_code
        == 200
    )
    assert member.get(f"/v1/orgs/{org}/audit").status_code == 200
    assert ("member.roles_updated", "success") in audit_actions(org)


def test_disabled_member_loses_access_immediately_and_can_be_restored() -> None:
    owner, org = _org_with_owner()
    member, _ = invite_and_join(owner, org, "op@exemple.fr", "operator")
    assert member.get(f"/v1/orgs/{org}").status_code == 200
    target = membership_id(owner, org, "op@exemple.fr")
    assert owner.post(f"/v1/orgs/{org}/members/{target}/disable").status_code == 200
    assert member.get(f"/v1/orgs/{org}").status_code == 404
    assert member.get("/v1/auth/me").json()["memberships"] == []
    assert owner.post(f"/v1/orgs/{org}/members/{target}/enable").status_code == 200
    assert member.get(f"/v1/orgs/{org}").status_code == 200


def test_owner_can_demote_a_co_owner_but_one_owner_always_remains() -> None:
    owner, org = _org_with_owner()
    invite_and_join(owner, org, "coproprio@exemple.fr", "org_owner")
    co = membership_id(owner, org, "coproprio@exemple.fr")
    assert (
        owner.put(f"/v1/orgs/{org}/members/{co}/roles", json={"roles": ["viewer"]}).status_code
        == 200
    )
    roles = {m["user"]["email"]: m["roles"] for m in owner.get(f"/v1/orgs/{org}/members").json()}
    assert roles["proprio@exemple.fr"] == ["org_owner"]


def test_only_owner_can_change_org_settings() -> None:
    owner, org = _org_with_owner()
    admin, _ = invite_and_join(owner, org, "admin@exemple.fr", "org_admin")
    assert admin.patch(f"/v1/orgs/{org}", json={"name": "Nom admin"}).status_code == 403
    r = owner.patch(
        f"/v1/orgs/{org}", json={"name": "Nom propriétaire", "timezone": "Europe/Paris"}
    )
    assert r.status_code == 200
    assert r.json()["timezone"] == "Europe/Paris"


def test_roles_catalog_reports_what_actor_may_assign() -> None:
    owner, org = _org_with_owner()
    admin, _ = invite_and_join(owner, org, "admin@exemple.fr", "org_admin")
    assignable = {r["key"]: r["assignable"] for r in admin.get(f"/v1/orgs/{org}/roles").json()}
    assert assignable == {
        "org_owner": False,
        "org_admin": False,
        "analyst": True,
        "operator": True,
        "viewer": True,
    }

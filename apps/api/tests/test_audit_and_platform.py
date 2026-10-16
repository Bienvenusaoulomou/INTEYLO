import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from app.cli import main as cli_main
from tests.conftest import APP_URL, Api, invite_and_join, org_id_of, owner_engine, signup


def test_audit_is_append_only_for_app_and_owner_roles() -> None:
    owner = Api()
    org = org_id_of(signup(owner, "proprio@exemple.fr"))
    app_engine = create_engine(APP_URL)
    for statement in ("update audit_events set action = 'x'", "delete from audit_events"):
        with app_engine.connect() as c, pytest.raises(DBAPIError, match="permission denied"):
            c.execute(text("select set_config('app.current_org_id', :o, false)"), {"o": org})
            c.execute(text(statement))
        with owner_engine.connect() as c, pytest.raises(DBAPIError, match="append-only"):
            c.execute(text(statement))


def test_owner_reads_audit_with_actor_and_no_secrets() -> None:
    owner = Api()
    org = org_id_of(signup(owner, "proprio@exemple.fr"))
    invite_and_join(owner, org, "membre@exemple.fr", "viewer")
    page = owner.get(f"/v1/orgs/{org}/audit?limit=10").json()
    actions = [e["action"] for e in page["items"]]
    assert {"organization.created", "invitation.created", "invitation.accepted"} <= set(actions)
    created = next(e for e in page["items"] if e["action"] == "invitation.created")
    assert created["actor_email"] == "proprio@exemple.fr"
    for event in page["items"]:
        assert not {"password", "token", "token_hash"} & set(event["details"])


def test_audit_pagination_bounds_are_validated_in_french() -> None:
    owner = Api()
    org = org_id_of(signup(owner, "proprio@exemple.fr"))
    r = owner.get(f"/v1/orgs/{org}/audit?limit=500")
    assert r.status_code == 422
    assert r.json()["error"]["details"] == [
        {"field": "limit", "message": "La valeur doit être inférieure ou égale à 200."}
    ]


def test_platform_routes_refuse_regular_users() -> None:
    api = Api()
    signup(api, "normal@exemple.fr")
    assert api.get("/v1/platform/organizations").status_code == 403


def test_platform_admin_can_suspend_but_not_read_org_data() -> None:
    owner = Api()
    org = org_id_of(signup(owner, "proprio@exemple.fr", org="Client X"))
    admin = Api()
    signup(admin, "root@inteylo.fr", org="INTEYLO interne")
    assert cli_main(["promote-platform-admin", "--email", "root@inteylo.fr"]) == 0

    listed = {o["name"]: o for o in admin.get("/v1/platform/organizations").json()}
    assert listed["Client X"]["active_members"] == 1
    # Pas d'accès aux données internes d'une organisation dont il n'est pas membre.
    assert admin.get(f"/v1/orgs/{org}/members").status_code == 404
    assert admin.get(f"/v1/orgs/{org}/audit").status_code == 404

    assert admin.post(f"/v1/platform/organizations/{org}/suspend").status_code == 200
    r = owner.get(f"/v1/orgs/{org}")
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "organization_suspended"
    assert admin.post(f"/v1/platform/organizations/{org}/reactivate").status_code == 200
    assert owner.get(f"/v1/orgs/{org}").status_code == 200
    with owner_engine.connect() as c:
        actions = (
            c.execute(
                text(
                    "select action from audit_events where org_id = :o and action like 'platform.%'"
                    " order by created_at"
                ),
                {"o": org},
            )
            .scalars()
            .all()
        )
    assert actions == ["platform.organization_suspended", "platform.organization_reactivated"]


def test_cli_reports_unknown_account(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli_main(["promote-platform-admin", "--email", "absent@exemple.fr"]) == 1
    assert "Aucun compte" in capsys.readouterr().err

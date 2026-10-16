from sqlalchemy import text

from tests.conftest import Api, audit_actions, org_id_of, owner_engine, signup


def _invite(owner: Api, org: str, email: str, role: str = "analyst") -> str:
    r = owner.post(f"/v1/orgs/{org}/invitations", json={"email": email, "role": role})
    assert r.status_code == 201, r.text
    url = r.json()["accept_url"]
    assert url.startswith("http://localhost:3000/invitation#")
    return str(url.split("#", 1)[1])


def _setup() -> tuple[Api, str]:
    owner = Api()
    return owner, org_id_of(signup(owner, "proprio@exemple.fr", org="Studio Nord"))


def test_inspect_then_accept_creates_account_and_membership() -> None:
    owner, org = _setup()
    token = _invite(owner, org, "Nina@Exemple.fr")
    preview = Api().post("/v1/invitations/inspect", json={"token": token}).json()
    assert preview["organization_name"] == "Studio Nord"
    assert preview["email"] == "nina@exemple.fr"
    assert preview["account_exists"] is False
    guest = Api()
    r = guest.post(
        "/v1/invitations/accept",
        json={"token": token, "full_name": "Nina", "password": "motdepasse-solide-789"},
    )
    assert r.status_code == 200
    assert r.json()["memberships"][0]["roles"] == ["analyst"]
    assert ("invitation.accepted", "success") in audit_actions(org)
    statuses = [i["status"] for i in owner.get(f"/v1/orgs/{org}/invitations").json()]
    assert statuses == ["accepted"]


def test_token_is_single_use() -> None:
    owner, org = _setup()
    token = _invite(owner, org, "omar@exemple.fr")
    body = {"token": token, "full_name": "Omar", "password": "motdepasse-solide-789"}
    assert Api().post("/v1/invitations/accept", json=body).status_code == 200
    r = Api().post("/v1/invitations/accept", json=body)
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "invitation_invalid"


def test_revoked_and_expired_invitations_are_rejected() -> None:
    owner, org = _setup()
    token = _invite(owner, org, "paul@exemple.fr")
    inv_id = owner.get(f"/v1/orgs/{org}/invitations").json()[0]["id"]
    assert owner.delete(f"/v1/orgs/{org}/invitations/{inv_id}").status_code == 200
    assert Api().post("/v1/invitations/inspect", json={"token": token}).status_code == 400

    token2 = _invite(owner, org, "quentin@exemple.fr")
    with owner_engine.begin() as c:
        c.execute(
            text(
                "update invitations set expires_at = now() - interval '1 minute'"
                " where email = 'quentin@exemple.fr'"
            )
        )
    r = Api().post(
        "/v1/invitations/accept",
        json={"token": token2, "full_name": "Q", "password": "motdepasse-solide-789"},
    )
    assert r.status_code == 400
    assert r.json()["error"]["message"].startswith("Cette invitation n'est plus valide")


def test_unknown_token_rejected() -> None:
    r = Api().post("/v1/invitations/inspect", json={"token": "x" * 43})
    assert r.status_code == 400


def test_existing_account_must_log_in_with_matching_email() -> None:
    owner, org = _setup()
    other = Api()
    signup(other, "rita@exemple.fr", org="Ailleurs")
    token = _invite(owner, org, "rita@exemple.fr")
    r = Api().post("/v1/invitations/accept", json={"token": token})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "invitation_login_required"

    intruder = Api()
    signup(intruder, "sam@exemple.fr", org="Intrus")
    r = intruder.post("/v1/invitations/accept", json={"token": token})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "invitation_email_mismatch"

    r = other.post("/v1/invitations/accept", json={"token": token})
    assert r.status_code == 200
    assert len(r.json()["memberships"]) == 2


def test_new_account_requires_name_and_password() -> None:
    owner, org = _setup()
    token = _invite(owner, org, "tom@exemple.fr")
    r = Api().post("/v1/invitations/accept", json={"token": token})
    assert r.status_code == 422
    assert {d["field"] for d in r.json()["error"]["details"]} == {"full_name", "password"}


def test_duplicate_pending_invitation_and_existing_member_rejected() -> None:
    owner, org = _setup()
    _invite(owner, org, "uma@exemple.fr")
    r = owner.post(
        f"/v1/orgs/{org}/invitations", json={"email": "uma@exemple.fr", "role": "viewer"}
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "invitation_pending"
    r = owner.post(
        f"/v1/orgs/{org}/invitations", json={"email": "proprio@exemple.fr", "role": "viewer"}
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "already_member"


def test_invitation_token_is_never_stored_or_audited_in_clear() -> None:
    owner, org = _setup()
    token = _invite(owner, org, "vera@exemple.fr")
    with owner_engine.connect() as c:
        dump = " ".join(
            str(v)
            for table in ("invitations", "audit_events")
            for row in c.execute(text(f"select * from {table}")).all()  # noqa: S608
            for v in row
        )
    assert token not in dump

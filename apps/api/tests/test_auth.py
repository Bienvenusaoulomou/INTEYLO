from tests.conftest import Api, signup


def test_signup_creates_owner_org_and_secure_cookie() -> None:
    api = Api()
    r = api.post(
        "/v1/auth/signup",
        json={
            "email": "Alice@Exemple.fr",
            "password": "motdepasse-solide-123",
            "full_name": "Alice Martin",
            "organization_name": "Atelier Alice",
            "timezone": "Africa/Tunis",
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["user"]["email"] == "alice@exemple.fr"
    assert body["memberships"][0]["roles"] == ["org_owner"]
    assert "users.manage" in body["memberships"][0]["permissions"]
    cookie = r.headers["set-cookie"]
    assert "inteylo_session=" in cookie
    assert "HttpOnly" in cookie
    assert "samesite=lax" in cookie.lower()
    assert api.get("/v1/auth/me").status_code == 200


def test_duplicate_email_rejected_in_french() -> None:
    signup(Api(), "bob@exemple.fr")
    r = Api().post(
        "/v1/auth/signup",
        json={
            "email": "BOB@exemple.fr",
            "password": "motdepasse-solide-123",
            "full_name": "Bob",
            "organization_name": "Autre",
        },
    )
    assert r.status_code == 409
    assert r.json()["error"] == {
        "code": "email_already_used",
        "message": "Un compte existe déjà avec cette adresse e-mail.",
        "details": [],
    }


def test_login_failure_is_generic_and_success_opens_session() -> None:
    signup(Api(), "carla@exemple.fr")
    api = Api()
    for email in ("carla@exemple.fr", "inconnu@exemple.fr"):
        r = api.post("/v1/auth/login", json={"email": email, "password": "mauvais-mot-de-passe"})
        assert r.status_code == 401
        assert r.json()["error"]["message"] == "Adresse e-mail ou mot de passe incorrect."
    r = api.post(
        "/v1/auth/login", json={"email": "carla@exemple.fr", "password": "motdepasse-solide-123"}
    )
    assert r.status_code == 200
    assert api.get("/v1/auth/me").json()["user"]["email"] == "carla@exemple.fr"


def test_login_rate_limited() -> None:
    signup(Api(), "dan@exemple.fr")
    api = Api()
    codes = [
        api.post("/v1/auth/login", json={"email": "dan@exemple.fr", "password": "x"}).status_code
        for _ in range(11)
    ]
    assert codes[:10] == [401] * 10
    assert codes[10] == 429
    # Même le bon mot de passe est refusé pendant le blocage.
    r = api.post(
        "/v1/auth/login", json={"email": "dan@exemple.fr", "password": "motdepasse-solide-123"}
    )
    assert r.status_code == 429
    assert r.json()["error"]["code"] == "too_many_attempts"


def test_logout_revokes_session_token() -> None:
    api = Api()
    signup(api, "eve@exemple.fr")
    token = api.cookies.get("inteylo_session")
    assert api.post("/v1/auth/logout").status_code == 200
    replay = Api()
    replay.cookies.set("inteylo_session", token)
    r = replay.get("/v1/auth/me")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "authentication_required"


def test_revoke_other_sessions() -> None:
    first = Api()
    signup(first, "fred@exemple.fr")
    second = Api()
    second.post(
        "/v1/auth/login", json={"email": "fred@exemple.fr", "password": "motdepasse-solide-123"}
    )
    sessions = first.get("/v1/auth/sessions").json()
    assert len(sessions) == 2
    assert sum(s["current"] for s in sessions) == 1
    assert first.post("/v1/auth/sessions/revoke-others").json() == {"revoked": 1}
    assert second.get("/v1/auth/me").status_code == 401
    assert first.get("/v1/auth/me").status_code == 200


def test_cannot_revoke_someone_elses_session() -> None:
    a, b = Api(), Api()
    signup(a, "gina@exemple.fr", org="Org A")
    signup(b, "hugo@exemple.fr", org="Org B")
    b_session = b.get("/v1/auth/sessions").json()[0]["id"]
    r = a.delete(f"/v1/auth/sessions/{b_session}")
    assert r.status_code == 404
    assert b.get("/v1/auth/me").status_code == 200


def test_unsafe_request_without_client_header_is_refused() -> None:
    api = Api()
    del api.client.headers["x-inteylo-client"]
    r = api.post("/v1/auth/login", json={"email": "a@b.fr", "password": "x"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "csrf_header_missing"


def test_deactivated_user_loses_access() -> None:
    from sqlalchemy import text

    from tests.conftest import owner_engine

    api = Api()
    signup(api, "ines@exemple.fr")
    with owner_engine.begin() as c:
        c.execute(text("update users set is_active = false where email = 'ines@exemple.fr'"))
    assert api.get("/v1/auth/me").status_code == 401
    r = Api().post(
        "/v1/auth/login", json={"email": "ines@exemple.fr", "password": "motdepasse-solide-123"}
    )
    assert r.status_code == 401

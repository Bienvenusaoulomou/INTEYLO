"""Règle linguistique côté API (prompt maître, section 13) et format des erreurs."""

import re

from sqlalchemy import create_engine

from app.core.db import check_database_role
from app.core.errors import ErrorCode
from app.core.messages_fr import MESSAGES
from tests.conftest import OWNER_URL, Api

# Mots anglais courants dans les messages par défaut de Pydantic/Starlette.
ENGLISH = re.compile(
    r"\b(field|required|value|should|must|invalid|string|not found|method|error|least|"
    r"character|input|expected|missing|unauthorized|forbidden|valid email)\b",
    re.IGNORECASE,
)


def _messages(payload: dict) -> list[str]:  # type: ignore[type-arg]
    err = payload["error"]
    return [err["message"], *(d["message"] for d in err["details"])]


def test_every_error_code_has_a_french_message() -> None:
    assert set(MESSAGES) == set(ErrorCode)
    for code, message in MESSAGES.items():
        assert message.strip(), code
        assert not ENGLISH.search(message), (code, message)


def test_validation_errors_are_translated() -> None:
    r = Api().post(
        "/v1/auth/signup",
        json={
            "email": "pas-un-email",
            "password": "court",
            "full_name": "",
            "organization_name": "X",
            "timezone": "Mars/Olympus",
            "inconnu": 1,
        },
    )
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "validation_error"
    details = {d["field"]: d["message"] for d in body["error"]["details"]}
    assert details == {
        "email": "Adresse e-mail invalide.",
        "password": "Ce champ doit contenir au moins 12 caractères.",
        "full_name": "Ce champ doit contenir au moins 1 caractères.",
        "organization_name": "Ce champ doit contenir au moins 2 caractères.",
        "timezone": "Fuseau horaire inconnu.",
        "inconnu": "Ce champ n'est pas autorisé.",
    }
    for message in _messages(body):
        assert not ENGLISH.search(message), message


def test_missing_fields_and_bad_uuid() -> None:
    api = Api()
    r = api.post("/v1/auth/login", json={})
    assert {d["message"] for d in r.json()["error"]["details"]} == {"Ce champ est obligatoire."}
    assert api.get("/v1/orgs/pas-un-uuid").status_code == 401  # authentification d'abord
    from tests.conftest import signup

    signup(api, "uuid@exemple.fr")
    r = api.get("/v1/orgs/pas-un-uuid")
    assert r.status_code == 422
    assert r.json()["error"]["details"][0]["message"] == "Identifiant invalide."


def test_malformed_json_unknown_route_and_method() -> None:
    api = Api()
    r = api.post(
        "/v1/auth/login", content=b"{pas du json", headers={"content-type": "application/json"}
    )
    assert r.status_code == 400
    assert r.json()["error"]["message"] == "La requête est mal formée."
    r = api.get("/v1/inexistant")
    assert r.status_code == 404
    assert r.json()["error"]["message"] == "Ressource introuvable."
    r = api.put("/v1/auth/me")
    assert r.status_code == 405
    assert r.json()["error"]["message"] == "Méthode non autorisée."


def test_unauthenticated_message_is_french() -> None:
    r = Api().get("/v1/auth/me")
    assert r.status_code == 401
    assert r.json()["error"]["message"] == (
        "Votre session a expiré ou n'existe pas. Veuillez vous reconnecter."
    )


def test_security_headers_and_health() -> None:
    api = Api()
    r = api.get("/health/live")
    assert r.json() == {"status": "ok"}
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["cache-control"] == "no-store"
    assert "x-request-id" in r.headers
    assert api.get("/health/ready").json() == {"status": "ok"}


def test_role_check_detects_unsafe_owner_connection() -> None:
    from sqlalchemy.orm import Session

    with Session(create_engine(OWNER_URL)) as db:
        assert check_database_role(db) == ["database role owns application tables"]

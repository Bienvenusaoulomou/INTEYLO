"""Alignement du backend sur le contrat partagé ``contracts/identity.json``."""

import json
import re
from pathlib import Path

from app.core.errors import ErrorCode
from app.modules.identity.rbac import (
    ORG_PERMISSIONS,
    ORG_ROLE_RANKS,
    PLATFORM_PERMISSIONS,
    PLATFORM_ROLE_RANKS,
)

ROOT = Path(__file__).resolve().parents[3]
CONTRACT = json.loads((ROOT / "contracts" / "identity.json").read_text(encoding="utf-8"))
APP_DIR = Path(__file__).resolve().parents[1] / "app"


def test_roles_and_permissions_match_contract() -> None:
    assert set(CONTRACT["organizationRoles"]) == set(ORG_ROLE_RANKS)
    assert set(CONTRACT["platformRoles"]) == set(PLATFORM_ROLE_RANKS)
    assert CONTRACT["organizationPermissions"] == list(ORG_PERMISSIONS)
    assert CONTRACT["platformPermissions"] == list(PLATFORM_PERMISSIONS)


def test_error_codes_match_contract() -> None:
    assert CONTRACT["errorCodes"] == [c.value for c in ErrorCode]


def test_every_audit_action_in_code_is_declared() -> None:
    source = "\n".join(p.read_text(encoding="utf-8") for p in APP_DIR.rglob("*.py"))
    literals = set(
        re.findall(
            r'"((?:auth|organization|permission|member|invitation|platform)'
            r'\.[a-z_]+)"',
            source,
        )
    )
    actions = {
        lit for lit in literals if not lit.startswith(("platform.organizations", "platform.audit"))
    }
    assert actions <= set(CONTRACT["auditActions"]), actions - set(CONTRACT["auditActions"])
    assert set(CONTRACT["auditActions"]) <= actions, set(CONTRACT["auditActions"]) - actions

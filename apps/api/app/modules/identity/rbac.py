"""Référentiel RBAC de la phase 1 (source de vérité documentaire).

La base de données est initialisée par la migration 0001 avec exactement ces valeurs ;
le test ``test_rbac_seed_matches_reference`` garantit qu'elles restent synchronisées.
Les libellés affichés sont dans le catalogue ``fr`` du frontend, jamais ici.
"""

ORG_ROLE_RANKS: dict[str, int] = {
    "org_owner": 100,
    "org_admin": 80,
    "analyst": 40,
    "operator": 40,
    "viewer": 10,
}
PLATFORM_ROLE_RANKS: dict[str, int] = {"platform_super_admin": 1000}
OWNER_ROLE = "org_owner"

ORG_PERMISSIONS: tuple[str, ...] = (
    "organizations.read",
    "organizations.manage",
    "users.read",
    "users.invite",
    "users.manage",
    "roles.read",
    "roles.manage",
    "connectors.read",
    "connectors.configure",
    "analytics.read",
    "analytics.run",
    "reports.create",
    "actions.propose",
    "actions.approve",
    "actions.execute",
    "memory.read",
    "memory.manage",
    "audit.read",
    "billing.manage",
)
PLATFORM_PERMISSIONS: tuple[str, ...] = (
    "platform.organizations.read",
    "platform.organizations.suspend",
    "platform.audit.read",
)

_READ_BASE = {"organizations.read", "analytics.read", "memory.read"}

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "org_owner": frozenset(ORG_PERMISSIONS),
    "org_admin": frozenset(set(ORG_PERMISSIONS) - {"organizations.manage", "billing.manage"}),
    "analyst": frozenset(
        _READ_BASE
        | {"users.read", "roles.read", "connectors.read", "analytics.run", "reports.create"}
        | {"actions.propose"}
    ),
    "operator": frozenset(
        _READ_BASE
        | {"users.read", "roles.read", "connectors.read", "actions.propose", "actions.execute"}
    ),
    "viewer": frozenset(_READ_BASE),
    "platform_super_admin": frozenset(PLATFORM_PERMISSIONS),
}

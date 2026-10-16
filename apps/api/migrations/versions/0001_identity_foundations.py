"""Fondations phase 1 : identité, organisations, RBAC, sessions, audit, RLS.

Revision ID: 0001
Revises:
Create Date: 2026-10-16
"""

import os

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

APP_ROLE = os.environ.get("INTEYLO_APP_DB_ROLE", "inteylo_app")

ORG_ROLES = [
    ("org_owner", "organization", 100),
    ("org_admin", "organization", 80),
    ("analyst", "organization", 40),
    ("operator", "organization", 40),
    ("viewer", "organization", 10),
    ("platform_super_admin", "platform", 1000),
]
ORG_PERMISSIONS = [
    "organizations.read", "organizations.manage", "users.read", "users.invite", "users.manage",
    "roles.read", "roles.manage", "connectors.read", "connectors.configure", "analytics.read",
    "analytics.run", "reports.create", "actions.propose", "actions.approve", "actions.execute",
    "memory.read", "memory.manage", "audit.read", "billing.manage",
]
PLATFORM_PERMISSIONS = [
    "platform.organizations.read", "platform.organizations.suspend", "platform.audit.read",
]
READ_BASE = ["organizations.read", "analytics.read", "memory.read"]
ROLE_PERMISSIONS = {
    "org_owner": ORG_PERMISSIONS,
    "org_admin": [p for p in ORG_PERMISSIONS if p not in ("organizations.manage", "billing.manage")],
    "analyst": READ_BASE + ["users.read", "roles.read", "connectors.read", "analytics.run",
                            "reports.create", "actions.propose"],
    "operator": READ_BASE + ["users.read", "roles.read", "connectors.read", "actions.propose",
                             "actions.execute"],
    "viewer": READ_BASE,
    "platform_super_admin": PLATFORM_PERMISSIONS,
}


def upgrade() -> None:
    op.execute(f"""
    DO $$ BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{APP_ROLE}') THEN
        CREATE ROLE {APP_ROLE} NOLOGIN;
      END IF;
    END $$;
    """)

    op.execute("""
    CREATE FUNCTION app_current_user() RETURNS uuid LANGUAGE sql STABLE AS
      $$ SELECT nullif(current_setting('app.current_user_id', true), '')::uuid $$;
    CREATE FUNCTION app_current_org() RETURNS uuid LANGUAGE sql STABLE AS
      $$ SELECT nullif(current_setting('app.current_org_id', true), '')::uuid $$;
    CREATE FUNCTION app_is_platform_admin() RETURNS boolean LANGUAGE sql STABLE AS
      $$ SELECT coalesce(current_setting('app.platform_admin', true), '') = 'on' $$;

    CREATE TABLE users (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      email varchar(320) NOT NULL UNIQUE CHECK (email = lower(email)),
      full_name varchar(200) NOT NULL,
      password_hash text NOT NULL,
      is_active boolean NOT NULL DEFAULT true,
      is_platform_admin boolean NOT NULL DEFAULT false,
      created_at timestamptz NOT NULL DEFAULT now()
    );

    CREATE TABLE sessions (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id uuid NOT NULL REFERENCES users(id),
      token_hash varchar(64) NOT NULL UNIQUE,
      created_at timestamptz NOT NULL DEFAULT now(),
      expires_at timestamptz NOT NULL,
      last_seen_at timestamptz NOT NULL,
      revoked_at timestamptz,
      ip_address varchar(64),
      user_agent varchar(300)
    );
    CREATE INDEX ix_sessions_user ON sessions(user_id);

    CREATE TABLE roles (
      key varchar(50) PRIMARY KEY,
      scope varchar(20) NOT NULL CHECK (scope IN ('organization', 'platform')),
      rank integer NOT NULL,
      is_system boolean NOT NULL DEFAULT true
    );
    CREATE TABLE permissions (
      key varchar(80) PRIMARY KEY,
      scope varchar(20) NOT NULL CHECK (scope IN ('organization', 'platform'))
    );
    CREATE TABLE role_permissions (
      role_key varchar(50) NOT NULL REFERENCES roles(key),
      permission_key varchar(80) NOT NULL REFERENCES permissions(key),
      PRIMARY KEY (role_key, permission_key)
    );

    CREATE TABLE organizations (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      name varchar(200) NOT NULL,
      status varchar(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended')),
      locale varchar(10) NOT NULL DEFAULT 'fr',
      timezone varchar(64) NOT NULL DEFAULT 'UTC',
      created_at timestamptz NOT NULL DEFAULT now()
    );

    CREATE TABLE memberships (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL REFERENCES organizations(id),
      user_id uuid NOT NULL REFERENCES users(id),
      status varchar(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'disabled')),
      created_at timestamptz NOT NULL DEFAULT now(),
      UNIQUE (org_id, user_id)
    );
    CREATE INDEX ix_memberships_user ON memberships(user_id);

    CREATE TABLE membership_roles (
      membership_id uuid NOT NULL REFERENCES memberships(id) ON DELETE CASCADE,
      role_key varchar(50) NOT NULL REFERENCES roles(key),
      org_id uuid NOT NULL REFERENCES organizations(id),
      PRIMARY KEY (membership_id, role_key)
    );
    CREATE INDEX ix_membership_roles_org ON membership_roles(org_id);

    CREATE TABLE invitations (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid NOT NULL REFERENCES organizations(id),
      email varchar(320) NOT NULL CHECK (email = lower(email)),
      role_key varchar(50) NOT NULL REFERENCES roles(key),
      token_hash varchar(64) NOT NULL UNIQUE,
      invited_by uuid NOT NULL REFERENCES users(id),
      created_at timestamptz NOT NULL DEFAULT now(),
      expires_at timestamptz NOT NULL,
      accepted_at timestamptz,
      revoked_at timestamptz
    );
    CREATE INDEX ix_invitations_org ON invitations(org_id);
    CREATE UNIQUE INDEX ux_invitations_pending ON invitations(org_id, email)
      WHERE accepted_at IS NULL AND revoked_at IS NULL;

    CREATE TABLE audit_events (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      org_id uuid REFERENCES organizations(id),
      actor_user_id uuid REFERENCES users(id),
      action varchar(100) NOT NULL,
      outcome varchar(20) NOT NULL CHECK (outcome IN ('success', 'denied', 'failure')),
      target_type varchar(50),
      target_id varchar(100),
      details jsonb NOT NULL DEFAULT '{}'::jsonb,
      ip_address varchar(64),
      created_at timestamptz NOT NULL DEFAULT now()
    );
    CREATE INDEX ix_audit_org_created ON audit_events(org_id, created_at DESC);

    -- Audit en ajout seul : aucune modification ni suppression, même par erreur applicative.
    CREATE FUNCTION audit_events_immutable() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      RAISE EXCEPTION 'audit_events is append-only';
    END $$;
    CREATE TRIGGER trg_audit_events_immutable BEFORE UPDATE OR DELETE ON audit_events
      FOR EACH ROW EXECUTE FUNCTION audit_events_immutable();
    """)

    # Référentiel RBAC.
    values = ", ".join(f"('{k}', '{s}', {r})" for k, s, r in ORG_ROLES)
    op.execute(f"INSERT INTO roles (key, scope, rank) VALUES {values}")
    perms = [(p, "organization") for p in ORG_PERMISSIONS] + [
        (p, "platform") for p in PLATFORM_PERMISSIONS
    ]
    op.execute(
        "INSERT INTO permissions (key, scope) VALUES "
        + ", ".join(f"('{p}', '{s}')" for p, s in perms)
    )
    pairs = [(r, p) for r, ps in ROLE_PERMISSIONS.items() for p in ps]
    op.execute(
        "INSERT INTO role_permissions (role_key, permission_key) VALUES "
        + ", ".join(f"('{r}', '{p}')" for r, p in pairs)
    )

    # Row Level Security : défense en profondeur contre un oubli de filtre applicatif.
    op.execute("""
    ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
    ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;
    ALTER TABLE membership_roles ENABLE ROW LEVEL SECURITY;
    ALTER TABLE invitations ENABLE ROW LEVEL SECURITY;
    ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
    ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

    CREATE POLICY memberships_select ON memberships FOR SELECT USING (
      org_id = app_current_org() OR user_id = app_current_user() OR app_is_platform_admin());
    CREATE POLICY memberships_insert ON memberships FOR INSERT
      WITH CHECK (org_id = app_current_org());
    CREATE POLICY memberships_update ON memberships FOR UPDATE
      USING (org_id = app_current_org()) WITH CHECK (org_id = app_current_org());

    CREATE POLICY organizations_select ON organizations FOR SELECT USING (
      id = app_current_org() OR app_is_platform_admin() OR EXISTS (
        SELECT 1 FROM memberships m
        WHERE m.org_id = organizations.id AND m.user_id = app_current_user()
          AND m.status = 'active'));
    CREATE POLICY organizations_insert ON organizations FOR INSERT
      WITH CHECK (id = app_current_org() AND app_current_user() IS NOT NULL);
    CREATE POLICY organizations_update ON organizations FOR UPDATE
      USING (id = app_current_org() OR app_is_platform_admin())
      WITH CHECK (id = app_current_org() OR app_is_platform_admin());

    CREATE POLICY membership_roles_select ON membership_roles FOR SELECT USING (
      org_id = app_current_org() OR app_is_platform_admin() OR EXISTS (
        SELECT 1 FROM memberships m
        WHERE m.id = membership_roles.membership_id AND m.user_id = app_current_user()));
    CREATE POLICY membership_roles_insert ON membership_roles FOR INSERT
      WITH CHECK (org_id = app_current_org());
    CREATE POLICY membership_roles_delete ON membership_roles FOR DELETE
      USING (org_id = app_current_org());

    CREATE POLICY invitations_all ON invitations FOR ALL
      USING (org_id = app_current_org()) WITH CHECK (org_id = app_current_org());

    CREATE POLICY audit_select ON audit_events FOR SELECT
      USING (org_id = app_current_org() OR app_is_platform_admin());
    CREATE POLICY audit_insert ON audit_events FOR INSERT
      WITH CHECK (org_id IS NULL OR org_id = app_current_org());

    CREATE POLICY sessions_own ON sessions FOR ALL
      USING (user_id = app_current_user()) WITH CHECK (user_id = app_current_user());

    -- Recherches par jeton haché, avant que l'utilisateur ou l'organisation ne soient connus.
    -- SECURITY DEFINER : exécutées avec les droits du propriétaire, qui n'est pas soumis à la RLS.
    CREATE FUNCTION session_lookup(p_token_hash text)
      RETURNS TABLE (session_id uuid, user_id uuid, expires_at timestamptz,
                     revoked_at timestamptz, last_seen_at timestamptz)
      LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public, pg_temp AS $$
        SELECT s.id, s.user_id, s.expires_at, s.revoked_at, s.last_seen_at
        FROM sessions s WHERE s.token_hash = p_token_hash
      $$;
    CREATE FUNCTION invitation_lookup(p_token_hash text)
      RETURNS TABLE (invitation_id uuid, org_id uuid)
      LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public, pg_temp AS $$
        SELECT i.id, i.org_id FROM invitations i WHERE i.token_hash = p_token_hash
      $$;
    REVOKE ALL ON FUNCTION session_lookup(text) FROM PUBLIC;
    REVOKE ALL ON FUNCTION invitation_lookup(text) FROM PUBLIC;
    """)

    op.execute(f"""
    GRANT USAGE ON SCHEMA public TO {APP_ROLE};
    GRANT SELECT, INSERT, UPDATE ON users, sessions, organizations, memberships, invitations
      TO {APP_ROLE};
    GRANT SELECT, INSERT, DELETE ON membership_roles TO {APP_ROLE};
    GRANT SELECT, INSERT ON audit_events TO {APP_ROLE};
    GRANT SELECT ON roles, permissions, role_permissions TO {APP_ROLE};
    GRANT EXECUTE ON FUNCTION app_current_user(), app_current_org(), app_is_platform_admin(),
      session_lookup(text), invitation_lookup(text) TO {APP_ROLE};
    """)


def downgrade() -> None:
    op.execute("""
    DROP FUNCTION IF EXISTS invitation_lookup(text);
    DROP FUNCTION IF EXISTS session_lookup(text);
    DROP TABLE IF EXISTS audit_events, invitations, membership_roles, memberships,
      organizations, role_permissions, permissions, roles, sessions, users CASCADE;
    DROP FUNCTION IF EXISTS audit_events_immutable();
    DROP FUNCTION IF EXISTS app_is_platform_admin();
    DROP FUNCTION IF EXISTS app_current_org();
    DROP FUNCTION IF EXISTS app_current_user();
    """)

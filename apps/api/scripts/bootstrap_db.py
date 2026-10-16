"""Prépare une base PostgreSQL locale pour INTEYLO, sans Docker.

Crée les deux rôles (propriétaire pour les migrations, applicatif soumis à la RLS), la base,
puis applique les migrations. Destiné au développement local et aux tests de bout en bout.

    python scripts/bootstrap_db.py \
        --admin-url postgresql+psycopg://postgres@127.0.0.1:5432/postgres \
        --database inteylo_dev [--reset]

Mots de passe : INTEYLO_DB_OWNER_PASSWORD et INTEYLO_DB_APP_PASSWORD (valeurs de développement
par défaut, refusées si --database contient « prod »). Affiche l'URL à utiliser pour l'API.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

API_DIR = Path(__file__).resolve().parents[1]
IDENT = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")
OWNER, APP = "inteylo_owner", "inteylo_app"


def _check(name: str) -> str:
    if not IDENT.match(name):
        raise SystemExit(f"Identifiant PostgreSQL invalide : {name!r}")
    return name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--admin-url", required=True, help="URL d'un superutilisateur PostgreSQL")
    parser.add_argument("--database", default="inteylo_dev")
    parser.add_argument("--reset", action="store_true", help="supprime et recrée la base")
    args = parser.parse_args()

    database = _check(args.database)
    owner_pw = os.environ.get("INTEYLO_DB_OWNER_PASSWORD", "owner-dev-password")
    app_pw = os.environ.get("INTEYLO_DB_APP_PASSWORD", "app-dev-password")
    dev_passwords = owner_pw.endswith("dev-password") or app_pw.endswith("dev-password")
    if "prod" in database and dev_passwords:
        raise SystemExit("Mots de passe de développement refusés pour une base de production.")

    admin = create_engine(args.admin_url, isolation_level="AUTOCOMMIT")
    with admin.connect() as c:
        for role, pw in ((OWNER, owner_pw), (APP, app_pw)):
            exists = c.execute(text("select 1 from pg_roles where rolname = :r"), {"r": role})
            verb = "ALTER" if exists.first() else "CREATE"
            # Le DDL n'accepte pas de paramètre lié : littéral échappé selon les règles SQL.
            literal = "'" + pw.replace("'", "''") + "'"
            c.execute(text(f"{verb} ROLE {role} LOGIN PASSWORD {literal}"))
        if args.reset:
            c.execute(text(f"DROP DATABASE IF EXISTS {database} WITH (FORCE)"))
        found = c.execute(text("select 1 from pg_database where datname = :d"), {"d": database})
        if not found.first():
            c.execute(text(f"CREATE DATABASE {database} OWNER {OWNER}"))
    admin.dispose()

    base = make_url(args.admin_url)
    owner_url = base.set(username=OWNER, password=owner_pw, database=database)
    app_url = base.set(username=APP, password=app_pw, database=database)
    env = {
        **os.environ,
        "INTEYLO_MIGRATION_DATABASE_URL": owner_url.render_as_string(hide_password=False),
        "INTEYLO_APP_DB_ROLE": APP,
    }
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"], cwd=API_DIR, env=env, check=True
    )
    print("Base prête. Variable à définir pour l'API :")
    print(f"INTEYLO_DATABASE_URL={app_url.render_as_string(hide_password=True)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

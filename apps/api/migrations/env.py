"""Environnement Alembic.

Les migrations s'exécutent avec le rôle propriétaire (INTEYLO_MIGRATION_DATABASE_URL),
jamais avec le rôle applicatif utilisé par l'API.
"""

import os
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool


def _url() -> str:
    file_var = os.environ.get("INTEYLO_MIGRATION_DATABASE_URL_FILE")
    if file_var:
        return Path(file_var).read_text(encoding="utf-8").strip()
    url = os.environ.get("INTEYLO_MIGRATION_DATABASE_URL")
    if not url:
        raise RuntimeError("INTEYLO_MIGRATION_DATABASE_URL est requis pour les migrations.")
    return url


def run_migrations_online() -> None:
    engine = create_engine(_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()

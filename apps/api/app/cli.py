"""Commandes d'exploitation.

    python -m app.cli promote-platform-admin --email admin@exemple.fr

L'opération est journalisée dans l'audit. Elle ne crée pas de compte : la personne doit
d'abord s'inscrire normalement.
"""

import argparse
import sys

from sqlalchemy import select

from app.core.db import get_session_factory, set_tenant_context
from app.modules.audit.service import record
from app.modules.identity.models import User


def promote_platform_admin(email: str) -> int:
    with get_session_factory()() as db, db.begin():
        user = db.scalar(select(User).where(User.email == email.lower()))
        if user is None:
            print("Aucun compte ne correspond à cette adresse e-mail.", file=sys.stderr)
            return 1
        set_tenant_context(db, user_id=user.id)
        user.is_platform_admin = True
        record(
            db,
            action="platform.admin_promoted",
            actor_user_id=None,
            target_type="user",
            target_id=user.id,
            details={"via": "cli"},
        )
    print("Le compte a été promu super-administrateur de la plateforme.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="inteylo")
    sub = parser.add_subparsers(dest="command", required=True)
    promote = sub.add_parser("promote-platform-admin")
    promote.add_argument("--email", required=True)
    args = parser.parse_args(argv)
    if args.command == "promote-platform-admin":
        return promote_platform_admin(args.email)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

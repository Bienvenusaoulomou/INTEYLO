#!/usr/bin/env bash
# Restauration d'une sauvegarde INTEYLO dans une base cible (nouvelle par défaut).
#   infrastructure/scripts/restore.sh <fichier.dump> [base_cible]
# La base cible est créée vide et appartient à inteylo_owner. La sauvegarde contient les GRANT
# vers inteylo_app et la table alembic_version : aucune migration n'est à rejouer.
# Les rôles inteylo_owner et inteylo_app doivent exister sur le serveur cible.
# Variables : PG_EXEC (voir backup.sh), PGUSER (superutilisateur, défaut postgres).
set -euo pipefail

FILE="${1:?fichier de sauvegarde requis}"
TARGET="${2:-inteylo_restore_$(date -u +%Y%m%d%H%M%S)}"
PG_EXEC="${PG_EXEC-docker compose exec -T postgres}"
SUPER="${PGUSER:-postgres}"

if [[ ! "$TARGET" =~ ^[a-z_][a-z0-9_]{0,62}$ ]]; then
  echo "Nom de base invalide : $TARGET" >&2
  exit 1
fi
if [[ -f "$FILE.sha256" ]]; then
  sha256sum --check --quiet "$FILE.sha256"
fi

# shellcheck disable=SC2086
$PG_EXEC psql -v ON_ERROR_STOP=1 -U "$SUPER" -d postgres -c "CREATE DATABASE $TARGET OWNER inteylo_owner"
# shellcheck disable=SC2086
$PG_EXEC pg_restore -U "$SUPER" -d "$TARGET" --no-owner --role=inteylo_owner --exit-on-error <"$FILE"
# shellcheck disable=SC2086
$PG_EXEC psql -v ON_ERROR_STOP=1 -U "$SUPER" -d postgres \
  -c "REVOKE ALL ON DATABASE $TARGET FROM PUBLIC" -c "GRANT CONNECT ON DATABASE $TARGET TO inteylo_app"
echo "Restauration terminée dans la base « $TARGET »."
echo "Pour basculer l'application : pointer INTEYLO_DB_NAME vers « $TARGET », puis redémarrer api."

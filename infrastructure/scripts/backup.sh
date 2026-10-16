#!/usr/bin/env bash
# Sauvegarde logique de la base INTEYLO (format personnalisé pg_dump, compressé).
#   infrastructure/scripts/backup.sh [dossier]        (par défaut ./backups)
# Variables :
#   PG_EXEC        préfixe d'exécution (défaut : "docker compose exec -T postgres" ; vide = outils locaux)
#   INTEYLO_DB_NAME  base à sauvegarder (défaut : inteylo)
#   BACKUP_GPG_RECIPIENT  si défini, chiffre la sauvegarde pour cette clé GPG
set -euo pipefail

DEST="${1:-./backups}"
DB="${INTEYLO_DB_NAME:-inteylo}"
PG_EXEC="${PG_EXEC-docker compose exec -T postgres}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
FILE="$DEST/inteylo-$DB-$STAMP.dump"

mkdir -p "$DEST"
umask 077
# shellcheck disable=SC2086
$PG_EXEC pg_dump -U "${PGUSER:-postgres}" -d "$DB" --format=custom --no-owner >"$FILE"

# Contrôle d'intégrité : l'archive doit être lisible par pg_restore.
# shellcheck disable=SC2086
$PG_EXEC pg_restore --list <"$FILE" >/dev/null

sha256sum "$FILE" >"$FILE.sha256"

if [[ -n "${BACKUP_GPG_RECIPIENT:-}" ]]; then
  gpg --batch --yes --encrypt --recipient "$BACKUP_GPG_RECIPIENT" --output "$FILE.gpg" "$FILE"
  rm -f "$FILE"
  echo "Sauvegarde chiffrée : $FILE.gpg"
else
  echo "Sauvegarde : $FILE (non chiffrée : définir BACKUP_GPG_RECIPIENT avant de l'exporter hors du serveur)"
fi

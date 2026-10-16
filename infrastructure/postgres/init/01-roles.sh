#!/usr/bin/env bash
# Exécuté une seule fois par l'image postgres, à l'initialisation du volume.
# Crée le rôle propriétaire (migrations) et le rôle applicatif (API, soumis à la RLS),
# puis la base INTEYLO. Les mots de passe sont lus depuis des fichiers de secrets.
set -euo pipefail

read_secret() {
  local file_var="$1_FILE" value_var="$1"
  if [[ -n "${!file_var:-}" ]]; then
    cat "${!file_var}"
  elif [[ -n "${!value_var:-}" ]]; then
    printf '%s' "${!value_var}"
  else
    echo "Secret manquant : $1 ou $1_FILE" >&2
    exit 1
  fi
}

OWNER_PASSWORD="$(read_secret INTEYLO_OWNER_PASSWORD)"
APP_PASSWORD="$(read_secret INTEYLO_APP_PASSWORD)"
DB="${INTEYLO_DB_NAME:-inteylo}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
  -v owner_pw="$OWNER_PASSWORD" -v app_pw="$APP_PASSWORD" -v db="$DB" <<'SQL'
CREATE ROLE inteylo_owner LOGIN PASSWORD :'owner_pw';
CREATE ROLE inteylo_app LOGIN PASSWORD :'app_pw' NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
CREATE DATABASE :"db" OWNER inteylo_owner;
REVOKE ALL ON DATABASE :"db" FROM PUBLIC;
GRANT CONNECT ON DATABASE :"db" TO inteylo_app;
SQL

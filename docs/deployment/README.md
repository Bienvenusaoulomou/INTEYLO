# Déploiement, sauvegarde et restauration

Cible initiale : un serveur Linux (2 vCPU, 4 Go de RAM au minimum) avec Docker Engine et le plugin Compose, un nom de domaine pointant vers le serveur, et les ports 80 et 443 ouverts.

## 1. Préparer le serveur

```bash
git clone <dépôt> /opt/inteylo && cd /opt/inteylo
mkdir -m 700 secrets
openssl rand -base64 32 > secrets/postgres_password
openssl rand -base64 32 > secrets/owner_password
openssl rand -base64 32 > secrets/app_password
# URLs complètes (les mots de passe générés ci-dessus, encodés si besoin) :
printf 'postgresql+psycopg://inteylo_owner:%s@postgres:5432/inteylo' "$(cat secrets/owner_password | jq -sRr @uri)" > secrets/migration_database_url
printf 'postgresql+psycopg://inteylo_app:%s@postgres:5432/inteylo'   "$(cat secrets/app_password   | jq -sRr @uri)" > secrets/database_url
chmod 600 secrets/*
```

Créer `.env` :

```bash
INTEYLO_DOMAIN=app.exemple.fr
INTEYLO_ACME_EMAIL=exploitation@exemple.fr
INTEYLO_IMAGE_PREFIX=ghcr.io/<compte>/inteylo
INTEYLO_VERSION=<sha du commit validé par la CI>
```

## 2. Démarrer

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

L'ordre est garanti par les dépendances : `postgres` sain → `migrate` terminé avec succès → `api` saine → `web` → `proxy`. Caddy obtient le certificat TLS au premier accès.

Vérification (smoke test) :

```bash
curl -fsS https://$INTEYLO_DOMAIN/api/health/ready     # {"status":"ok"}
curl -fsS -o /dev/null -w '%{http_code}\n' https://$INTEYLO_DOMAIN/   # 200
```

## 3. Mettre à jour et revenir en arrière

```bash
# Mise à jour : nouvelle version validée par la CI
sed -i 's/^INTEYLO_VERSION=.*/INTEYLO_VERSION=<nouveau sha>/' .env
infrastructure/scripts/backup.sh /var/backups/inteylo        # toujours avant une migration
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Retour arrière (images immuables, taguées par SHA)
sed -i 's/^INTEYLO_VERSION=.*/INTEYLO_VERSION=<sha précédent>/' .env
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Si la version annulée contenait une migration non rétrocompatible, restaurer la sauvegarde prise juste avant (section 5). Règle de développement : les migrations sont additives (ajout de colonnes et de tables), la suppression se fait dans une version ultérieure.

## 4. Sauvegarde

```bash
BACKUP_GPG_RECIPIENT=exploitation@exemple.fr infrastructure/scripts/backup.sh /var/backups/inteylo
```

Le script produit un `pg_dump` au format personnalisé, vérifie qu'il est lisible, calcule son SHA-256, puis le chiffre avec GPG si un destinataire est défini. Planification quotidienne (cron de l'hôte) :

```cron
15 2 * * * cd /opt/inteylo && BACKUP_GPG_RECIPIENT=exploitation@exemple.fr infrastructure/scripts/backup.sh /var/backups/inteylo && find /var/backups/inteylo -mtime +30 -delete
```

Copier ensuite les fichiers `.gpg` hors du serveur (stockage objet d'un autre fournisseur ou d'une autre région).

## 5. Restauration

```bash
gpg --decrypt inteylo-inteylo-<date>.dump.gpg > /tmp/restore.dump
infrastructure/scripts/restore.sh /tmp/restore.dump inteylo_restore
```

La restauration crée une **nouvelle** base (aucun écrasement), avec les mêmes propriétaires, droits, politiques RLS et version de migration. Pour basculer : définir `INTEYLO_DB_NAME=inteylo_restore` et remplacer le nom de la base dans `secrets/database_url` et `secrets/migration_database_url`, puis relancer `docker compose ... up -d api migrate`.

**Test réalisé le 16/10/2026** (base de bout en bout, PostgreSQL 17) : 6 utilisateurs, 3 organisations, 20 événements d'audit et la version de migration `0001` restaurés à l'identique. Les tables restaurées appartiennent à `inteylo_owner`, la RLS est active, et le rôle applicatif ne voit aucune organisation sans contexte. À rejouer chaque trimestre sur une sauvegarde de production.

## 6. Promouvoir un super-administrateur

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api \
  python -m app.cli promote-platform-admin --email admin@exemple.fr
```

L'opération est journalisée (`platform.admin_promoted`).

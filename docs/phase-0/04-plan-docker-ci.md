# Phase 0 — Plan Docker et CI/CD

## 1. Conteneurs

| Service | Image | Utilisateur | Exposition | Santé |
|---|---|---|---|---|
| `proxy` | `caddy:2` — route `/api/*` vers l'API (préfixe retiré) et le reste vers le web | défaut de l'image | 80, 443 (production uniquement) | — |
| `web` | `apps/web/Dockerfile` — Next.js `output: standalone`, Node 22 slim | `nextjs` (1001) | réseau `app` | `GET /` |
| `api` | `apps/api/Dockerfile` — Python 3.13 slim, multi-étapes, dépendances de `requirements.lock` | `inteylo` (10001) | réseau `app` + `data` | `GET /health/ready` |
| `migrate` | même image que `api`, commande `alembic upgrade head` | `inteylo` | réseau `data` | sort en 0 |
| `postgres` | `postgres:17` | `postgres` | réseau `data` (`internal: true`), aucun port publié en production | `pg_isready` |
| `worker` | même image que `api` — ajouté en phase 2 | `inteylo` | `app` + `data` | — |

Fichiers :

- `docker-compose.yml` (racine) : développement. Le port 5432 est publié sur `127.0.0.1` uniquement, l'API répond sur `localhost:8000` et le web sur `localhost:3000`.
- `docker-compose.prod.yml` (racine) : surcharge de production. Le proxy Caddy est actif, aucun port n'est publié hors du proxy et les secrets sont lus depuis des fichiers.
- `infrastructure/postgres/init/01-roles.sh` : crée le rôle applicatif `inteylo_app`, sans privilège de propriétaire, pour que la RLS s'applique.
- `.env.example` : la liste complète des variables, sans aucune valeur secrète.

Les secrets passent par les variables `INTEYLO_*_FILE` et les secrets Docker. Aucun secret n'est intégré à une image.

## 2. Pipeline (GitHub Actions — `.github/workflows/ci.yml`)

| # | Étape (§17) | Outil | Bloquant |
|---|---|---|---|
| 1 | Checkout | `actions/checkout` (permissions `contents: read`) | — |
| 2 | Formatage et lint | `ruff format --check`, `ruff check`, `eslint --max-warnings=0` | oui |
| 3 | Contrôle linguistique | `eslint-plugin-i18next` + `scripts/check-i18n.mjs` + `test_language_and_errors.py` | oui |
| 4 | Types | `mypy --strict`, `tsc --noEmit` | oui |
| 5–7 | Tests unitaires, intégration, RBAC et multi-tenant | `pytest` contre un service PostgreSQL 17, `vitest` | oui |
| 8 | Analyse statique | `bandit`, `semgrep` (règles `p/python`, `p/typescript`) | oui (sévérité élevée) |
| 9 | Secrets | `gitleaks` | oui |
| 10 | Dépendances | `pip-audit`, `npm audit --audit-level=high` | oui |
| 11 | Build des images | `docker buildx` (cache GHA) | oui |
| 12 | Scan des images | `trivy image --severity HIGH,CRITICAL --exit-code 1` | oui |
| 13 | Rapports | artefacts : couverture, SARIF | — |
| 14 | Publication | GHCR, tag = SHA du commit, uniquement sur `main` après succès | — |
| 15–20 | Staging, smoke tests, approbation, production, vérification, rollback | `deploy.yml`, environnements GitHub protégés | prévu en phase 7 |

Tests de bout en bout Playwright : job séparé. Il démarre l'API et le web contre PostgreSQL et teste les parcours ainsi que l'absence de texte anglais.

## 3. Ce qui reste à vérifier hors de cet environnement

Ici, les registres d'images sont inaccessibles. Les fichiers Docker sont validés par `docker compose config`, mais la construction et le démarrage réels des images doivent être confirmés sur un poste équipé de Docker Desktop ou par la CI GitHub.

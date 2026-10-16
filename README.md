# INTEYLO

Plateforme SaaS d'intelligence opérationnelle multi-tenant : données reliées, décisions justifiées, actions vérifiées, mémoire décisionnelle.

> **État : fin de phase 1 (fondations sécurisées).** Comptes, organisations, invitations, rôles et permissions, isolation entre organisations (applicative et PostgreSQL RLS), journal d'audit, console de plateforme, interface 100 % française. Les connecteurs, l'ingestion, l'IA, les actions et la mémoire décisionnelle relèvent des phases 2 à 5 et **ne sont pas encore implémentés**. Voir `docs/phase-0/06-backlog.md` et `docs/release/rapport-phase-1.md`.

## Structure

```
apps/api/          API FastAPI (monolithe modulaire), migrations Alembic, tests pytest
apps/web/          Interface Next.js, catalogue messages/fr.json, tests Vitest et Playwright
contracts/         Contrat partagé API ↔ interface (rôles, permissions, codes d'erreur, états)
infrastructure/    Initialisation PostgreSQL, Caddy
docs/              Prompt maître, phase 0, architecture, décisions (ADR), connecteurs, exploitation
docker-compose.yml / docker-compose.prod.yml
```

## Démarrer avec Docker (recommandé)

Prérequis : Docker Desktop (Windows, macOS) ou Docker Engine (Linux).

```bash
cp .env.example .env          # puis remplacer les trois mots de passe
docker compose up --build
```

- Interface : http://localhost:3000
- API et documentation interactive : http://localhost:8000/docs

Promouvoir un compte super-administrateur de la plateforme, après son inscription :

```bash
docker compose exec api python -m app.cli promote-platform-admin --email vous@exemple.fr
```

## Démarrer sans Docker (Windows, PowerShell)

Prérequis : **Python 3.13** (`winget install Python.Python.3.13`), Node.js 22 ou plus, PostgreSQL 16 ou plus en service local.

```powershell
# 1. API
cd apps\api
py -3.13 -m venv .venv
.\.venv\Scripts\pip install -r requirements.lock -e ".[dev]"
.\.venv\Scripts\python scripts\bootstrap_db.py --admin-url "postgresql+psycopg://postgres:<mdp>@127.0.0.1:5432/postgres" --database inteylo_dev
$env:INTEYLO_DATABASE_URL = "postgresql+psycopg://inteylo_app:app-dev-password@127.0.0.1:5432/inteylo_dev"
$env:INTEYLO_COOKIE_SECURE = "false"
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000

# 2. Interface (second terminal)
cd apps\web
npm ci
$env:API_INTERNAL_URL = "http://127.0.0.1:8000"
npm run dev
```

Sous Linux et macOS, les commandes sont identiques avec `.venv/bin/` et `export VAR=valeur`.

## Contrôles qualité

| Contrôle | API (`apps/api`) | Interface (`apps/web`) |
|---|---|---|
| Formatage et lint | `ruff format --check . && ruff check .` | `npm run lint` |
| Langue française | `pytest tests/test_language_and_errors.py` | `npm run i18n:check` |
| Types | `mypy app` | `npm run typecheck` |
| Tests | `pytest` (PostgreSQL requis, voir `docs/testing/README.md`) | `npm test`, `npm run test:e2e` |
| Sécurité | `bandit -r app -ll`, `pip-audit -r requirements.lock` | `npm audit --omit=dev` |

La CI GitHub Actions (`.github/workflows/ci.yml`) exécute l'ensemble, plus Gitleaks, Semgrep, la construction et le scan Trivy des images, puis la publication sur GHCR.

## Documentation

| Sujet | Emplacement |
|---|---|
| Spécification de référence | `docs/prompt/PROMPT_MAITRE_v2.1.md` |
| Analyse, RBAC, modèle de données, risques, backlog, glossaire | `docs/phase-0/` |
| Diagrammes UML et architectures | `docs/architecture/` (sources `.puml`, `.mmd` ; rendus dans `rendu/`) |
| Décisions d'architecture | `docs/decisions/` |
| API (OpenAPI) | `docs/api/` |
| Connecteurs et protocole d'ingestion signée | `docs/connectors/` |
| Tests | `docs/testing/README.md` |
| Déploiement, sauvegarde, restauration | `docs/deployment/README.md` |
| Exploitation et dépannage | `docs/operations/README.md` |
| Sécurité | `docs/security/README.md` |

## Règle de langue

Tout texte visible par un utilisateur est en français et provient du catalogue `apps/web/messages/fr.json` ou des messages d'API `apps/api/app/core/messages_fr.py`. Les identifiants techniques restent en anglais. La CI bloque toute violation (§14 du prompt maître).

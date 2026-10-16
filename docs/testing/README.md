# Tests

## Vue d'ensemble

| Suite | Emplacement | Outil | Base de données |
|---|---|---|---|
| API : authentification, RBAC, isolation, invitations, audit, langue, contrat | `apps/api/tests/` | pytest | PostgreSQL réel, migrations réelles, rôle applicatif sous RLS |
| Interface : formats `Intl`, client API, glossaire | `apps/web/tests/unit/` | Vitest | — |
| Bout en bout : parcours et absence de texte anglais | `apps/web/tests/e2e/` | Playwright (Chromium) | PostgreSQL réel via l'API |
| Contrôle linguistique du catalogue | `apps/web/scripts/check-i18n.mjs` | Node | — |

Aucun test ne simule la base de données : l'isolation entre organisations n'a de valeur que vérifiée contre PostgreSQL et la RLS.

## Tests de l'API

La suite crée une base `inteylo_test`, deux rôles (`inteylo_owner_test`, `inteylo_app_test`), applique les migrations, puis exécute les requêtes avec le rôle applicatif.

```bash
cd apps/api
export INTEYLO_TEST_ADMIN_URL=postgresql+psycopg://postgres:<mdp>@127.0.0.1:5432/postgres
pytest            # ou : pytest --cov=app
```

PowerShell : `$env:INTEYLO_TEST_ADMIN_URL = "..."`. Par défaut, l'URL vise `127.0.0.1:5433`.

## Tests de bout en bout

```bash
cd apps/api
python scripts/bootstrap_db.py --admin-url postgresql+psycopg://postgres:<mdp>@127.0.0.1:5432/postgres --database inteylo_e2e --reset
cd ../web
npx playwright install chromium        # une seule fois
E2E_DATABASE_URL=postgresql+psycopg://inteylo_app:app-dev-password@127.0.0.1:5432/inteylo_e2e npm run test:e2e
```

Playwright démarre lui-même l'API (port 8000) et un build de production Next.js (port 3100). `E2E_API_PYTHON` désigne l'interpréteur de l'API (par défaut `../api/.venv/bin/python` ; sous Windows : `..\api\.venv\Scripts\python.exe`).

## Ce que vérifient les tests de sécurité

- Accès d'un membre à une autre organisation, par l'API **et** par une requête SQL directe sous le rôle applicatif.
- Élévation verticale : un analyste qui tente d'inviter, de modifier un rôle ou de lire l'audit.
- Auto-promotion, attribution d'un rôle de rang égal ou supérieur, retrait du dernier propriétaire.
- Révocation : session révoquée ou membre désactivé, refusés à la requête suivante.
- Invitations : jeton réutilisé, expiré, révoqué, ou utilisé par un autre e-mail.
- Rôle de base de données dangereux (superutilisateur, BYPASSRLS, propriétaire) détecté.
- Requête modifiante sans en-tête anti-CSRF refusée.
- Chaque code d'erreur possède un message français ; les erreurs Pydantic sont traduites.

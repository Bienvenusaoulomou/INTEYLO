# Phase 0 — Livrables de la Phase 1

| # | Livrable | Emplacement | Vérification |
|---|---|---|---|
| 1 | API d'identité, d'organisations, d'invitations et de plateforme | `apps/api/app/modules/` | `pytest` (60 tests) |
| 2 | Migration initiale avec RLS et audit immuable | `apps/api/migrations/versions/0001_identity_foundations.py` | appliquée à chaque exécution de tests sur PostgreSQL 17 |
| 3 | Contrat partagé backend ↔ frontend | `contracts/identity.json` | `test_contracts.py`, `scripts/check-i18n.mjs` |
| 4 | Messages d'API en français | `apps/api/app/core/messages_fr.py` | `test_language_and_errors.py` |
| 5 | Interface française des écrans de phase 1 | `apps/web/src/` | `tsc`, `eslint`, `next build` |
| 6 | Catalogue `fr` | `apps/web/messages/fr.json` | `npm run i18n:check` |
| 7 | Tests unitaires web | `apps/web/tests/unit/` | `npm test` |
| 8 | Tests de bout en bout | `apps/web/tests/e2e/` | `npm run test:e2e` |
| 9 | Dockerfiles, compose de développement et de production | `apps/*/Dockerfile`, `docker-compose*.yml`, `infrastructure/` | `docker compose config` ; construction en CI |
| 10 | Pipeline CI | `.github/workflows/ci.yml` | exécution sur GitHub |
| 11 | Documentation | `README.md`, `CONTRIBUTING.md`, `docs/` | relecture |
| 12 | Rapport de lot | `docs/release/rapport-phase-1.md` | — |

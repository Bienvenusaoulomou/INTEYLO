# ADR-0001 — Stack technique

Statut : accepté · 16/10/2026

## Contexte

Le prompt maître (§4) propose React/Next.js/TypeScript pour le frontend, Python/FastAPI/SQLAlchemy/Alembic pour le backend et PostgreSQL pour les données. Le dépôt était vide : aucune contrainte héritée.

## Décision

| Couche | Choix | Version épinglée | Motif |
|---|---|---|---|
| Frontend | Next.js (App Router) + React + TypeScript strict | 16.4 / 19.3 / 5.9 | Rendu serveur, routage par fichiers, écosystème mature |
| Catalogue de traduction | next-intl | 4.14 | Messages ICU (pluriels, variables), formats `Intl`, compatible serveur et client |
| Tests web | Vitest, Playwright | 5.0 / 1.56 | Rapides ; Playwright vérifie les parcours réels |
| Backend | Python 3.13 + FastAPI + Pydantic 2 | 0.143 / 2.14 | Typage, validation, écosystème IA et données |
| ORM et migrations | SQLAlchemy 2 + Alembic | 2.1 / 1.20 | Migrations versionnées, SQL brut possible pour la RLS |
| Base | PostgreSQL 17 | 17 | RLS, JSONB, recherche plein texte, extensions vectorielles plus tard |
| Mots de passe | Argon2id (`argon2-cffi`) | 25.1 | Recommandation OWASP |
| Qualité | Ruff, mypy strict, ESLint, Bandit | — | Contrôles statiques bloquants |

Volontairement **absents** pour l'instant :

- **Redis** : le limiteur de tentatives fonctionne en mémoire tant qu'il n'y a qu'une instance d'API ; Redis viendra avec la file de tâches (B-14, B-23).
- **Bibliothèque de composants** : la phase 1 compte peu d'écrans. Des composants maison accessibles suffisent (`src/components/ui.tsx`). Le choix sera réexaminé en phase 6.
- **Courtier de messages** : à décider en phase 2. Options : file sur PostgreSQL (`SKIP LOCKED`) ou Redis.

## Conséquences

- Le poste Windows de développement dispose de Python 3.11 : il faut Python 3.13, ou Docker, pour lancer l'API localement (voir `README.md`).
- Une seule pile de langages par couche : pas de microservices tant que la charge ne le justifie pas (ADR-0002).

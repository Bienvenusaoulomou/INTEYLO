# Rapport de lot — Phase 0 et Phase 1

Date : 16/10/2026 · Référence : prompt maître v2.1 · Format : §22.

## 1. Objectif et périmètre

- **Phase 0** : intégrer toutes les corrections du prompt maître (v2.1), produire les douze livrables de conception, retirer Wix du périmètre.
- **Phase 1** : fondations sécurisées. Identité, organisations, RBAC, isolation multi-tenant, audit, interface française, Docker, CI, documentation.

## 2. Décisions d'architecture

ADR-0001 (stack), ADR-0002 (monolithe modulaire), ADR-0003 (isolation applicative + RLS), ADR-0004 (protocole d'ingestion signée générique, abandon de Wix), ADR-0005 (sessions opaques).

## 3. Fichiers principaux

| Domaine | Fichiers |
|---|---|
| Spécification | `docs/prompt/PROMPT_MAITRE_v2.1.md` (remplace la v1.1) |
| Phase 0 | `docs/phase-0/01` à `08`, `docs/architecture/*.puml`, `*.mmd`, `rendu/*.svg`, `docs/decisions/ADR-0001` à `0005`, `docs/connectors/` |
| API | `apps/api/app/`, `migrations/versions/0001_identity_foundations.py`, `scripts/bootstrap_db.py`, `Dockerfile` |
| Interface | `apps/web/src/`, `messages/fr.json`, `scripts/check-i18n.mjs`, `eslint.config.mjs`, `tests/unit/`, `tests/e2e/`, `playwright.config.ts`, `Dockerfile` |
| Infrastructure | `docker-compose.yml`, `docker-compose.prod.yml`, `infrastructure/postgres/init/01-roles.sh`, `infrastructure/caddy/Caddyfile`, `infrastructure/scripts/backup.sh`, `restore.sh`, `.env.example` |
| CI | `.github/workflows/ci.yml` |
| Documentation | `README.md`, `CONTRIBUTING.md`, `docs/{api,testing,deployment,operations,security,release}/` |

## 4. Commandes exécutées et résultats réels

Environnement : Linux, Python 3.13, Node 22, PostgreSQL 17.

| Contrôle | Commande | Résultat |
|---|---|---|
| Formatage, lint API | `ruff format --check . && ruff check .` | 40 fichiers conformes, 0 erreur |
| Types API | `mypy app` (strict) | 0 erreur, 29 fichiers |
| Tests API | `pytest --cov=app` | **60 réussis**, 0 échec, couverture **95 %** |
| Sécurité API | `bandit -r app -ll` ; `pip-audit -r requirements.lock --strict` | 0 alerte ; 0 vulnérabilité connue |
| Lint web (textes littéraux interdits) | `npm run lint` | 0 erreur, 0 avertissement ; un texte littéral de test est bien détecté |
| Contrôle linguistique | `npm run i18n:check` | 249 libellés, 158 usages, 81 identifiants du contrat couverts ; un catalogue piégé (anglais, valeur vide, clé manquante) est bien rejeté |
| Types web | `npm run typecheck` | 0 erreur |
| Tests unitaires web | `npm test` | **14 réussis** |
| Build de production | `next build` | réussi, 11 routes |
| Bout en bout | `npm run test:e2e` (vraie API, vrai PostgreSQL, build de production) | **4 réussis** : accueil, erreur de connexion, erreur de validation, parcours inscription → invitation → analyste aux droits limités, avec vérification « aucun texte anglais » à chaque écran |
| Audit npm | `npm audit --omit=dev --audit-level=high` | 0 vulnérabilité |
| Compose | `docker compose config` (dev, prod) | valides ; en production, seul le proxy publie des ports |
| Image API (simulée) | venv vierge depuis `requirements.lock`, Uvicorn en mode production | `/health/ready` 200, `/docs` 404, refus anti-CSRF en français |
| Initialisation PostgreSQL | `01-roles.sh` sur un cluster vierge, puis migrations | rôles sans privilège, base créée, mot de passe contenant une apostrophe accepté |
| Sauvegarde et restauration | `backup.sh` puis `restore.sh` | données, version de migration, propriétaires, RLS et droits restaurés à l'identique |
| Diagrammes | PlantUML | 5 diagrammes rendus sans erreur |

## 5. Problèmes détectés et corrigés pendant le lot

- `globals.css` absent : le build de production échouait. Feuille de style écrite et build réussi.
- Deux libellés du catalogue s'écartaient du glossaire (`EXECUTING`, `conversion`) : alignés, avec un test qui compare désormais le catalogue au glossaire.
- Le diagramme de déploiement contenait une erreur de syntaxe PlantUML : réécrit d'après les fichiers Compose réels.
- La documentation mentionnait une colonne `slug` inexistante : corrigée.
- Le script de rôles utilisait un paramètre lié dans un `CREATE ROLE`, ce que PostgreSQL refuse : remplacé par un littéral échappé.

## 6. Éléments non vérifiés ici, et pourquoi

| Élément | Raison | Où le vérifier |
|---|---|---|
| Construction et démarrage réels des images Docker | Registres d'images bloqués dans l'environnement de développement | CI GitHub (job `images`) ou Docker Desktop |
| Semgrep, Gitleaks, Trivy | Registres de règles et d'images bloqués | CI GitHub |
| Exécution de la CI GitHub elle-même | Dépôt pas encore poussé sur GitHub | Après création du dépôt distant |

## 7. Statut

| Terminé | En cours | Simulé | Non implémenté |
|---|---|---|---|
| Phase 0 complète ; phase 1 : B-01 à B-13 | — | Aucun | Connecteurs, ingestion, IA, actions, mémoire (phases 2 à 5) ; B-14 à B-16 |

Aucun connecteur n'est présenté comme opérationnel (voir `docs/connectors/inventaire.md`).

## 8. Risques et limites restantes

Limiteur de tentatives en mémoire (B-14) ; pas d'e-mails sortants donc pas de réinitialisation de mot de passe (B-15) ; images Docker à construire en CI (R11) ; premier portefeuille de connecteurs à choisir (R12).

## 9. Étapes suivantes (Phase 2)

1. Décisions attendues : premier portefeuille de connecteurs, fournisseur d'e-mails, hébergement du dépôt (GitHub).
2. B-20 à B-26 : modèle `Connection`, coffre de secrets, protocole d'ingestion signée v1.1 avec sa batterie de tests, worker, imports CSV, JSON et Excel, écrans du centre des connecteurs.

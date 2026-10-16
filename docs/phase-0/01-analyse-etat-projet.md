# Phase 0 — Analyse de l'état du projet

Date : 16 octobre 2026 · Référence : prompt maître v2.1 (`docs/prompt/PROMPT_MAITRE_v2.1.md`)

## 1. Point de départ

| Élément | Constat |
|---|---|
| Dépôt de code | Vide. Aucun code INTEYLO n'existait avant ce lot ; la structure initiale est créée ici. |
| Documents de référence | Blueprint maître v1.0 (15/10/2026), prompt maître v1.0, v1.1, v2.0 puis v2.1 (16/10/2026). |
| Connecteur Wix | Abandonné. Le document « Connecteur Wix → INTEYLO : protocole d'ingestion v1 » reste une base utile : ses règles (HMAC, idempotence, accusés, états `VERIFIED`/`UNCERTAIN`, isolation par locataire) deviennent le protocole générique de tous les connecteurs entrants (voir ADR-0004). Aucun code Wix n'est conservé. |
| Première source de données | Non choisie. Le portefeuille initial du blueprint (commerce + paiements, publicité, collaboration, import CSV/XLSX) reste à arbitrer. Bloquant pour la phase 2, pas pour la phase 1. |

## 2. Environnement de développement observé

Ces constats concernent l'environnement dans lequel ce lot a été produit. Ils déterminent ce qui a pu être réellement vérifié.

| Outil | Disponibilité | Conséquence |
|---|---|---|
| Python 3.13, Node 22 | Disponibles | Backend et frontend construits et testés. |
| PostgreSQL 17 | Pas de paquet système ; binaires officiels installés depuis le registre npm (`@embedded-postgres/linux-x64`) | Tests d'intégration exécutés contre un vrai PostgreSQL 17, avec RLS. |
| Poste Windows de l'utilisateur | Git, Node 24, Python 3.11, PostgreSQL (scoop) ; **pas de Docker** | Le dépôt y est copié ; l'API exige Python 3.13 ou Docker Desktop pour tourner localement. |
| Docker | Démon démarrable, mais tous les registres d'images (Docker Hub, GHCR, ECR, GCR) sont bloqués | Dockerfiles et `docker-compose.yml` écrits et validés syntaxiquement (`docker compose config`), **mais aucune image n'a pu être construite ni démarrée ici**. À vérifier sur un poste ou une CI disposant d'un accès aux registres. |
| PlantUML, Graphviz | Disponibles | Diagrammes `.puml` rendus et vérifiés. |
| Navigateurs Playwright | Non vérifiés | Tests de bout en bout écrits ; exécution prévue en CI. |

## 3. Hypothèses retenues

1. Produit SaaS multi-tenant hébergé par INTEYLO ; une organisation cliente = un tenant.
2. Inscription en libre-service : une personne crée son compte et son organisation, dont elle devient propriétaire.
3. Interface 100 % en français dès le lancement (section 14 du prompt maître) ; identifiants internes en anglais.
4. Monolithe modulaire FastAPI + workers ; un seul frontend Next.js.
5. Hébergement initial sur un serveur Linux avec Docker Compose ; passage à plusieurs machines quand la charge le justifie.
6. Pas encore de fournisseur d'identité externe (SSO) : authentification par e-mail et mot de passe, sessions opaques révocables. Le SSO est prévu au backlog.
7. Envoi d'e-mails non disponible en phase 1 : le lien d'invitation est affiché une seule fois à la personne qui invite, qui le transmet par un canal de confiance. Le jeton est placé après le `#` de l'URL, donc jamais envoyé au serveur ni écrit dans ses journaux.

## 4. Exigences de la phase 1 (rappel)

- Création d'une organisation et de son propriétaire.
- Invitation d'un utilisateur et acceptation.
- Attribution et modification de rôles dans les limites déléguées.
- Connexion, déconnexion, révocation de session.
- Accès aux ressources limité au tenant, au niveau applicatif **et** au niveau de la base (RLS).
- Journal d'audit en ajout seul, y compris pour les refus.
- Messages d'API en français, catalogue `fr` côté interface, contrôles linguistiques automatisés.
- Tests automatisés de sécurité (isolation, élévation de privilèges, révocation).

## 5. Ce que ce lot ne couvre pas

Connecteurs, ingestion, graphe métier, métriques, IA, actions et mémoire décisionnelle relèvent des phases 2 à 4. Ils sont représentés dans les diagrammes et le modèle de données cible, mais aucun code n'est livré pour eux.

## 6. Livrables de la Phase 0

| # | Livrable | Fichier |
|---|---|---|
| 1 | Analyse de l'état du projet | ce document |
| 2 | Architecture logique et physique | `docs/architecture/logical-architecture.mmd`, `physical-architecture.mmd`, `component-diagram.puml`, `deployment-diagram.puml` |
| 3 | Diagramme de cas d'utilisation | `docs/architecture/use-case-diagram.puml` |
| 4 | Modèle de données initial | `03-modele-donnees.md`, `docs/architecture/domain-model.puml` |
| 5 | Matrice RBAC | `02-matrice-rbac.md` |
| 6 | Plan Docker et CI/CD | `04-plan-docker-ci.md` |
| 7 | Risques | `05-risques.md` |
| 8 | Backlog | `06-backlog.md` |
| 9 | Décision sur la stack | `docs/decisions/ADR-0001-stack.md` (+ ADR-0002 à 0005) |
| 10 | Livrables de la Phase 1 | `08-livrables-phase-1.md` |
| 11 | Catalogue `fr` initial | `apps/web/messages/fr.json` |
| 12 | Glossaire d'affichage | `07-glossaire.md` |

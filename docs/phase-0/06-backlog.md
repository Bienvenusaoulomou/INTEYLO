# Phase 0 — Backlog ordonné

Statuts : ✅ fait et testé · 🟡 en cours · ⬜ à faire · ⛔ bloqué par une décision ou un accès externe.

## Phase 1 — Fondations sécurisées

| ID | Élément | Critères d'acceptation | Statut |
|---|---|---|---|
| B-01 | Inscription : création du compte et de l'organisation | L'utilisateur devient propriétaire ; e-mail unique ; mot de passe ≥ 12 caractères ; audit `auth.signup` | ✅ |
| B-02 | Connexion, déconnexion, sessions | Cookie `HttpOnly` ; liste des sessions ; révocation d'une session ou de toutes les autres ; limitation des tentatives | ✅ |
| B-03 | Isolation multi-tenant | Aucun accès à une autre organisation, ni par l'API ni par une requête SQL directe sous le rôle applicatif | ✅ |
| B-04 | RBAC et délégation | Matrice `02-matrice-rbac.md` appliquée ; auto-promotion et dernier propriétaire protégés | ✅ |
| B-05 | Invitations | Lien à usage unique, expirable et révocable ; e-mail lié ; acceptation par un compte existant ou nouveau | ✅ |
| B-06 | Journal d'audit | Ajout seul ; refus journalisés ; consultation paginée avec `audit.read` | ✅ |
| B-07 | Console plateforme | Liste et suspension d'organisations sans accès aux données métier | ✅ |
| B-08 | Erreurs d'API en français | `code` stable + `message` français ; erreurs Pydantic traduites | ✅ |
| B-09 | Interface française des écrans de phase 1 | Connexion, inscription, invitation, espace, organisation, membres, audit, compte, plateforme | ✅ |
| B-10 | Contrôles linguistiques du frontend | ESLint i18next (JSX et attributs visibles) + script de catalogue bloquant | ✅ |
| B-11 | Tests frontend | Vitest (formats, client API, catalogue) ; Playwright (parcours inscription → invitation → rôles, absence d'anglais) | ✅ |
| B-12 | Docker | Dockerfiles non-root, compose dev et prod, santé, rôle applicatif sous RLS | ✅ (construction réelle à confirmer en CI) |
| B-13 | CI GitHub Actions | Étapes 1 à 14 du §17, bloquantes | ✅ (écrite ; première exécution après envoi sur GitHub) |
| B-14 | Limiteur partagé | Limitation des tentatives stockée dans Redis lorsque plusieurs instances d'API tournent | ⬜ |
| B-15 | Réinitialisation du mot de passe | Lien à usage unique ; nécessite un fournisseur d'e-mails | ⛔ choix du fournisseur |
| B-16 | Accès d'assistance « bris de glace » | Accès temporaire, motivé, approuvé et audité | ⬜ |

## Phase 2 — Framework des connecteurs

| ID | Élément | Critères d'acceptation | Statut |
|---|---|---|---|
| B-20 | Modèle `Connection` + registre des connecteurs | 10 statuts du §7.2 ; aucun statut « connecté » sans test réel | ⬜ |
| B-21 | Coffre de secrets | Chiffrement AES-GCM avec clé hors base ; rotation ; jamais renvoyé au frontend | ⬜ |
| B-22 | Protocole d'ingestion signée v1.1 | Trois routes ; tests : signature invalide, horodatage expiré, rejeu, doublon, conflit d'empreinte, empreinte falsifiée, accès croisé | ⬜ |
| B-23 | Worker et file de tâches | Synchronisations hors requête HTTP ; reprises bornées | ⬜ |
| B-24 | Import CSV, JSON, Excel | Aperçu, correspondance des colonnes, rapport d'erreurs en français | ⬜ |
| B-25 | `SourceRecord` + règles d'ordre et de suppression | Un enregistrement ancien n'écrase pas un plus récent ; suppression propagée et auditée | ⬜ |
| B-26 | Écrans : catalogue, configuration, état des synchronisations | — | ⬜ |

## Phase 3 et suivantes

| ID | Élément | Statut |
|---|---|---|
| B-30 | Premier portefeuille de connecteurs natifs (proposition : Stripe, Shopify, Google Analytics 4, HubSpot) | ⛔ validation métier + comptes développeur |
| B-40 | Modèle canonique, Business Graph, registre des indicateurs, preuves | ⬜ |
| B-45 | Couche IA et assistant en français | ⛔ choix du fournisseur et budget |
| B-50 | Moteur d'actions, approbations, vérification, mémoire décisionnelle | ⬜ |
| B-60 | Interface complète (19 écrans du §14.6) | ⬜ |
| B-70 | Staging, sauvegarde et restauration testées, publication | ⬜ |

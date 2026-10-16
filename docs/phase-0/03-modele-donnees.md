# Phase 0 — Modèle de données initial

Diagramme : `docs/architecture/domain-model.puml` (rendu : `docs/architecture/rendu/INTEYLO_modele_domaine.svg`).

## 1. Implémenté (migration `0001_identity_foundations`)

| Table | Rôle | Tenant | RLS |
|---|---|---|---|
| `users` | Identité globale (une personne peut appartenir à plusieurs organisations) | — | non : accès via le service d'identité uniquement |
| `sessions` | Sessions opaques ; seul le SHA-256 du jeton est stocké | — | oui (`user_id` courant) |
| `organizations` | Tenant : nom, statut, `locale` (`fr` par défaut), `timezone` (`UTC` par défaut) | elle-même | oui |
| `memberships` | Lien utilisateur ↔ organisation, statut actif ou désactivé | `org_id` | oui |
| `roles`, `permissions`, `role_permissions` | Référentiel RBAC versionné par migration | — | lecture seule |
| `membership_roles` | Rôles attribués à une appartenance | via `memberships` | oui |
| `invitations` | Invitation à usage unique : jeton haché, expiration, révocation | `org_id` | oui |
| `audit_events` | Journal en ajout seul, refus compris | `org_id` (nul pour la plateforme) | oui + déclencheur d'immuabilité |

Contraintes notables : e-mail unique en minuscules ; une seule invitation en attente par (organisation, e-mail) ; clés étrangères partout ; horodatages `timestamptz`.

## 2. Cible des phases 2 à 5

Chaque table porte `org_id NOT NULL`, une politique RLS sur `org_id = current_setting('app.current_org_id')`, et un index composite commençant par `org_id`.

| Entité | Champs clés | Phase |
|---|---|---|
| `Connection` | type de source, statut (10 états du §7.2), scopes accordés, dernière synchronisation, identifiant public pour l'ingestion signée | 2 |
| `ConnectorCredentialReference` | référence vers le secret chiffré (jamais le secret en clair), date de rotation | 2 |
| `ConnectorCapability` | lectures et actions déclarées, quotas, réversibilité | 2 |
| `SyncJob`, `SyncRun` | planification, curseur incrémental, compteurs, erreurs | 2 |
| `IngestDelivery` | `(connection_id, delivery_id)` unique, empreinte JCS, état `ACCEPTED/VERIFIED/UNCERTAIN/DUPLICATE/REJECTED`, raison | 2 |
| `SourceRecord` | `(connection_id, external_type, external_id)` unique, `occurred_at`, `source_version`, charge brute, `deleted_at` | 2 |
| `CanonicalEntity` | type (client, commande, paiement, campagne…), attributs normalisés, devise explicite | 4 |
| `EntityLink` | paire d'entités, règle, confiance, statut `proposé / confirmé / rejeté`, justification | 4 |
| `MetricDefinition`, `MetricObservation` | formule, unité, devise, fuseau, période, version ; valeur datée + `EvidenceReference` | 4 |
| `EvidenceReference` | source, période, transformation, version des données | 4 |
| `Insight` | indicateur, période, référence de comparaison, méthode, confiance | 4 |
| `ActionPlan`, `ActionExecution`, `Approval`, `Workflow` | 11 états du §12, clé d'idempotence, approbateur, résultat de vérification | 5 |
| `Decision`, `MemoryEntry` | catégorie (factuelle, contextuelle, décisionnelle, résultat), provenance, validité, rétention | 5 |
| `Notification`, `UsageRecord` | — | 5 |

## 3. Règles transverses

- Montants : `numeric(20,6)` + `currency char(3)` obligatoire ; jamais de flottants.
- Temps : `timestamptz` ; le fuseau d'affichage est celui de l'organisation.
- Suppression : logique (`deleted_at`) pour `SourceRecord` et les entités dérivées, puis purge physique selon la durée de conservation ; propagation tracée (§8 du prompt maître).
- Données personnelles : collecte minimale ; aucun secret dans les tables métier ni dans l'audit.

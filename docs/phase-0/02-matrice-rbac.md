# Phase 0 — Matrice RBAC

Source de vérité : `apps/api/app/modules/identity/rbac.py`. La migration `0001` initialise la base avec exactement ces valeurs. Le test `test_rbac_seed_matches_reference` échoue si le code et la base divergent. Les libellés affichés proviennent du catalogue `apps/web/messages/fr.json` (glossaire : `07-glossaire.md`).

## 1. Rôles

| Clé interne | Libellé affiché | Portée | Rang |
|---|---|---|---|
| `platform_super_admin` | Super-administrateur de la plateforme | plateforme | 1000 |
| `org_owner` | Propriétaire de l'organisation | organisation | 100 |
| `org_admin` | Administrateur de l'organisation | organisation | 80 |
| `analyst` | Analyste | organisation | 40 |
| `operator` | Opérateur | organisation | 40 |
| `viewer` | Lecteur | organisation | 10 |

« Approbateur » n'est pas un rôle. C'est la permission `actions.approve`, détenue par les propriétaires et les administrateurs, et attribuable à d'autres rôles quand des rôles personnalisés seront disponibles.

## 2. Permissions d'organisation

✓ = accordé · — = refusé

| Permission | Propriétaire | Administrateur | Analyste | Opérateur | Lecteur |
|---|:-:|:-:|:-:|:-:|:-:|
| `organizations.read` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `organizations.manage` | ✓ | — | — | — | — |
| `users.read` | ✓ | ✓ | ✓ | ✓ | — |
| `users.invite` | ✓ | ✓ | — | — | — |
| `users.manage` | ✓ | ✓ | — | — | — |
| `roles.read` | ✓ | ✓ | ✓ | ✓ | — |
| `roles.manage` | ✓ | ✓ | — | — | — |
| `connectors.read` | ✓ | ✓ | ✓ | ✓ | — |
| `connectors.configure` | ✓ | ✓ | — | — | — |
| `analytics.read` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `analytics.run` | ✓ | ✓ | ✓ | — | — |
| `reports.create` | ✓ | ✓ | ✓ | — | — |
| `actions.propose` | ✓ | ✓ | ✓ | ✓ | — |
| `actions.approve` | ✓ | ✓ | — | — | — |
| `actions.execute` | ✓ | ✓ | — | ✓ | — |
| `memory.read` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `memory.manage` | ✓ | ✓ | — | — | — |
| `audit.read` | ✓ | ✓ | — | — | — |
| `billing.manage` | ✓ | — | — | — | — |

## 3. Permissions de plateforme

| Permission | Super-administrateur |
|---|:-:|
| `platform.organizations.read` | ✓ (métadonnées uniquement : nom, statut, nombre de membres) |
| `platform.organizations.suspend` | ✓ |
| `platform.audit.read` | ✓ (événements de plateforme) |

Le super-administrateur n'a **aucune** permission d'organisation. Il ne lit ni les membres, ni les données métier, ni l'audit d'une organisation cliente. Un accès d'assistance passera par une procédure « bris de glace » auditée, prévue au backlog (B-16).

## 4. Règles de délégation (appliquées côté serveur)

1. Personne ne modifie ses propres rôles.
2. On ne peut attribuer, retirer ou désactiver que des rôles d'un rang **strictement inférieur** au sien. Seul un propriétaire peut nommer un autre propriétaire.
3. Une organisation conserve toujours au moins un propriétaire actif.
4. Un administrateur d'organisation ne peut ni lire ni modifier les rôles de plateforme.
5. La désactivation d'un membre révoque immédiatement ses sessions pour cette organisation : la requête suivante est refusée.
6. Chaque refus d'autorisation produit un événement d'audit `outcome = denied`.

## 5. Défense en profondeur

| Couche | Mécanisme |
|---|---|
| API | Dépendance `require_permission(...)` sur chaque route ; tenant extrait du chemin et comparé à l'appartenance active. |
| Base | RLS PostgreSQL sur `organizations`, `memberships`, `membership_roles`, `invitations`, `sessions`, `audit_events`. L'API se connecte avec un rôle sans privilège de propriétaire et positionne `app.current_user_id` et `app.current_org_id` par transaction. Le démarrage échoue si le rôle contourne la RLS (`check_database_role`). |
| Audit | Table en ajout seul : un déclencheur refuse `UPDATE` et `DELETE`. |
| Interface | Masque les commandes non autorisées, sans que cela vaille autorisation. |

## 6. Tests associés

`apps/api/tests/test_rbac.py`, `test_tenant_isolation.py`, `test_invitations.py`, `test_audit_and_platform.py` couvrent l'élévation verticale, l'accès horizontal entre organisations (API **et** requêtes directes sous RLS), l'auto-promotion, la révocation et le dernier propriétaire.

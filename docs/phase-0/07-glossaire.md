# Phase 0 — Glossaire d'affichage

Référence : prompt maître v2.1, §14.5. Ce glossaire est la seule source des libellés visibles pour les rôles, les modules et les états. Le catalogue `apps/web/messages/fr.json` l'applique ; toute divergence est un défaut.

## Rôles

| Interne | Affiché | Clé du catalogue |
|---|---|---|
| `platform_super_admin` | Super-administrateur de la plateforme | `roles.platform_super_admin` |
| `org_owner` | Propriétaire de l'organisation | `roles.org_owner` |
| `org_admin` | Administrateur de l'organisation | `roles.org_admin` |
| `analyst` | Analyste | `roles.analyst` |
| `operator` | Opérateur | `roles.operator` |
| `viewer` | Lecteur | `roles.viewer` |
| permission `actions.approve` | Approbateur | `roles.approver` |

## États des actions

| Interne | Affiché |
|---|---|
| `REQUESTED` | Demandée |
| `POLICY_CHECKED` | Contrôlée |
| `AWAITING_APPROVAL` | En attente d'approbation |
| `APPROVED` | Approuvée |
| `REJECTED` | Refusée |
| `EXECUTING` | En cours |
| `EXECUTED` | Exécutée |
| `VERIFIED` | Vérifiée |
| `FAILED` | Échouée |
| `UNCERTAIN` | Résultat incertain |
| `CANCELLED` | Annulée |

## États des connecteurs (§7.2)

| Interne | Affiché |
|---|---|
| `available` | Disponible à configurer |
| `incomplete` | Configuration incomplète |
| `auth_required` | Authentification requise |
| `connected` | Connecté |
| `syncing` | Synchronisation en cours |
| `synced` | Synchronisation réussie |
| `sync_error` | Erreur de synchronisation |
| `auth_expired` | Autorisation expirée |
| `limited` | Fonctionnalités limitées par le fournisseur |
| `disabled` | Désactivé |

## Modules

| Interne | Affiché |
|---|---|
| Workspace | Espace de travail |
| Dashboard | Tableau de bord |
| Connector Hub | Centre des connecteurs |
| Business Graph | Graphe métier |
| Metric Registry | Référentiel des indicateurs |
| Evidence Engine | Preuves et sources |
| Opportunity Radar | Radar d'opportunités |
| Decision Simulator | Simulateur de décisions |
| Action Engine | Actions |
| Approval Center | Centre d'approbation |
| Decision Memory | Mémoire décisionnelle |
| Audit & Incident Center | Audit et incidents |
| Marketing Intelligence | Marketing |
| Social Hub | Réseaux sociaux |
| Conversion Intelligence | Conversions |
| CRM & Sales | Ventes et relation client |
| Support Intelligence | Support client |
| Project & Operations | Projets et opérations |
| Finance & Billing | Finance et facturation |
| Predictive Intelligence | Prévisions |
| Insight | Constat |
| Workflow | Processus |

## Statuts divers (phase 1)

| Interne | Affiché |
|---|---|
| organisation `active` / `suspended` | Active / Suspendue |
| appartenance `active` / `disabled` | Actif / Désactivé |
| audit `success` / `denied` / `failure` | Réussi / Refusé / Échec |

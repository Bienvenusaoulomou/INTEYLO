# ADR-0003 — Isolation multi-tenant : contrôle applicatif + Row-Level Security

Statut : accepté · 16/10/2026

## Contexte

Une fuite entre organisations est l'incident le plus grave possible (blueprint, §9). Un oubli de filtre `org_id` dans une seule requête suffirait à la provoquer si l'isolation reposait uniquement sur le code applicatif.

## Décision

1. **Contrôle applicatif.** Chaque route d'organisation résout l'appartenance active de l'utilisateur au tenant du chemin, puis vérifie la permission requise.
2. **RLS PostgreSQL.** Toutes les tables portant des données d'organisation activent la RLS. Les politiques comparent `org_id` à `current_setting('app.current_org_id')` et l'utilisateur à `app.current_user_id`, positionnés par transaction (`set_config(..., true)`, équivalent de `SET LOCAL`).
3. **Deux rôles de base.** Le rôle propriétaire (`inteylo_owner`) exécute les migrations. Le rôle applicatif (`inteylo_app`) n'est ni superutilisateur, ni `BYPASSRLS`, ni propriétaire des tables. L'API vérifie ces conditions au démarrage et sur `/health/ready`.
4. **Tests négatifs aux deux niveaux.** Ils passent par l'API et par des requêtes SQL directes sous le rôle applicatif.

## Conséquences

Toute nouvelle table métier doit inclure `org_id`, sa politique RLS et un test d'isolation. La revue de code le vérifie.

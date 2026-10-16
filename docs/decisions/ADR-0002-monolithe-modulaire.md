# ADR-0002 — Monolithe modulaire et workers

Statut : accepté · 16/10/2026

## Décision

Une seule application FastAPI (`apps/api`) organisée en modules (`app/modules/<domaine>`), plus des workers qui réutilisent la même image et le même code, pour les tâches longues : synchronisations, workflows, calculs.

Règles :

1. Un module expose ses opérations par un service ou un routeur ; les autres modules n'accèdent pas directement à ses tables.
2. Le contexte de sécurité (utilisateur, organisation, permissions) est résolu une fois par requête (`identity.deps`) et transmis explicitement.
3. Les modules ne s'importent pas en boucle. `audit` et `core` sont des dépendances descendantes autorisées pour tous.
4. Une extraction en service séparé exige une mesure : charge, isolation de pannes, cadence de déploiement.

## Conséquences

Un seul déploiement et une seule base au départ. Les frontières sont documentées dans `docs/architecture/component-diagram.puml`.

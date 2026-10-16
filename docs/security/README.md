# Sécurité

Synthèse des mesures en place à la fin de la phase 1. Les décisions détaillées figurent dans `docs/decisions/`.

## Authentification et sessions (ADR-0005)

- Mots de passe : Argon2id, 12 caractères minimum ; message d'échec identique pour un compte inconnu ou un mauvais mot de passe.
- Session opaque de 256 bits dans un cookie `HttpOnly`, `SameSite=Lax`, `Secure` hors développement ; seul le SHA-256 du jeton est stocké ; durée configurable (7 jours par défaut).
- Révocation unitaire ou globale ; désactivation d'un membre ou d'un compte effective à la requête suivante.
- Anti-CSRF : en-tête `X-Inteylo-Client` obligatoire sur `POST`, `PUT`, `PATCH`, `DELETE`.
- Limitation des tentatives de connexion et d'inscription.

## Autorisations et isolation (ADR-0003)

- RBAC côté serveur sur chaque route ; matrice dans `docs/phase-0/02-matrice-rbac.md`.
- Délégation par rang strict ; aucune auto-modification ; dernier propriétaire protégé.
- RLS PostgreSQL sur toutes les tables d'organisation ; l'API utilise un rôle sans privilège et vérifie ce point au démarrage.
- Une ressource d'une autre organisation renvoie `404`, jamais `403` : l'existence n'est pas révélée.
- Le super-administrateur gère les organisations sans accéder à leurs données.

## Invitations

Jeton à usage unique de 256 bits, haché en base, jamais journalisé ; placé dans le fragment `#` de l'URL afin de ne jamais atteindre les journaux du serveur ; expiration (72 h) et révocation ; lié à l'adresse e-mail invitée.

## Audit

Table en ajout seul (déclencheur refusant `UPDATE` et `DELETE`, y compris pour le propriétaire des tables) ; refus d'accès journalisés ; aucun secret dans `details`.

## En-têtes HTTP

API : `X-Content-Type-Options`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store`, `X-Request-Id`, sans en-tête `Server`. Interface : CSP stricte en production (`default-src 'self'`, `frame-ancestors 'none'`), `X-Frame-Options: DENY`, `Permissions-Policy`. Proxy : HSTS.

## Conteneurs

Utilisateurs non-root (10001 pour l'API, 1001 pour le web), système de fichiers en lecture seule, `cap_drop: ALL`, `no-new-privileges`, base sur un réseau interne sans port publié en production, secrets montés en fichiers.

## Chaîne d'approvisionnement

Dépendances épinglées (`requirements.lock`, `package-lock.json`) ; CI : Bandit, Semgrep, Gitleaks, pip-audit, npm audit, Trivy ; images taguées par SHA et immuables.

## Résultats observés le 16/10/2026

| Contrôle | Résultat | Où |
|---|---|---|
| Bandit (sévérité moyenne et plus) | 0 alerte | local |
| pip-audit `requirements.lock` | 0 vulnérabilité connue | local |
| npm audit (production, seuil élevé) | 0 vulnérabilité | local |
| Semgrep, Gitleaks, Trivy | non exécutés : registres de règles et d'images inaccessibles depuis l'environnement de développement | CI GitHub |

## Limites connues

- Le limiteur de tentatives est en mémoire : à déplacer vers Redis avant de lancer plusieurs instances d'API (B-14).
- Pas encore de réinitialisation du mot de passe par e-mail (B-15), ni de double authentification, ni de SSO.
- Pas encore de procédure d'accès « bris de glace » pour l'assistance (B-16).

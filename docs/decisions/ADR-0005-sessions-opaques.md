# ADR-0005 — Sessions opaques en base plutôt que JWT

Statut : accepté · 16/10/2026

## Décision

L'authentification utilise un jeton aléatoire de 256 bits, envoyé dans un cookie `HttpOnly`, `SameSite=Lax` et `Secure` hors développement. Seul son SHA-256 est stocké (table `sessions`). Chaque requête vérifie la session en base.

Pour se protéger du CSRF, les requêtes modifiantes doivent porter l'en-tête `X-Inteylo-Client`, qu'un formulaire tiers ne peut pas ajouter, en plus de `SameSite`.

## Motifs

- Révocation immédiate : déconnexion, désactivation d'un membre, compromission. Le prompt maître l'exige (§6).
- Aucun secret de signature à faire tourner ; aucun jeton exploitable stocké côté navigateur hors cookie.
- Coût d'une lecture indexée par requête, acceptable à l'échelle visée.

## Conséquences

Le SSO (OIDC) viendra s'ajouter comme méthode de connexion produisant la même session opaque.

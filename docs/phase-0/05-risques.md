# Phase 0 — Risques techniques et de sécurité

Échelle : probabilité (P) et impact (I) de 1 à 3.

| # | Risque | P | I | Réponse | Statut |
|---|---|:-:|:-:|---|---|
| R1 | Fuite de données entre organisations | 2 | 3 | Contrôle applicatif + RLS PostgreSQL + tests négatifs API et SQL ; vérification au démarrage que le rôle de l'API ne contourne pas la RLS | Couvert en phase 1, à étendre à chaque nouvelle table |
| R2 | Élévation de privilèges par délégation de rôles | 2 | 3 | Règle de rang strict, interdiction de l'auto-modification, dernier propriétaire protégé, audit des refus | Couvert et testé |
| R3 | Vol de session ou CSRF | 2 | 3 | Cookie `HttpOnly`, `SameSite=Lax`, `Secure` hors développement ; en-tête `X-Inteylo-Client` exigé sur les requêtes modifiantes ; sessions révocables | Couvert et testé |
| R4 | Force brute sur la connexion | 2 | 2 | Limitation par couple (IP, e-mail) sur une fenêtre glissante, Argon2id, message d'erreur identique | Couvert ; limiteur en mémoire, à déplacer vers Redis en multi-instance (B-14) |
| R5 | Secrets dans le dépôt ou les images | 2 | 3 | `.env.example` sans valeur, fichiers de secrets, `gitleaks` en CI, `.dockerignore` | Couvert par la CI |
| R6 | Rejeu, falsification ou mauvais aiguillage des webhooks entrants | 2 | 3 | Protocole d'ingestion signée v1.1 (en-tête de connexion signé, corps brut, nonce, empreinte JCS recalculée) | Spécifié ; implémentation en phase 2 |
| R7 | Connecteurs déclarés « opérationnels » sans validation réelle | 3 | 2 | Statuts précis, tests simulés séparés des tests réels, inventaire de validation | Règle posée ; s'applique dès la phase 2 |
| R8 | Hallucinations de l'assistant | 3 | 3 | Calculs déterministes, preuves obligatoires, abstention en cas d'incertitude | Phase 4 |
| R9 | Actions dupliquées après un délai d'attente | 2 | 3 | Idempotence, état `UNCERTAIN`, vérification auprès du fournisseur avant toute reprise | Phase 5 |
| R10 | Texte anglais visible | 2 | 2 | Lint i18next, contrôle du catalogue, messages d'API en français, tests E2E | Couvert en CI |
| R11 | Écart entre l'environnement de développement et la production (Docker non vérifié ici) | 3 | 2 | Validation `docker compose config` ici, construction réelle en CI ; documentation des écarts | Ouvert : à confirmer en CI |
| R12 | Périmètre très large (vingt-cinq connecteurs, huit moteurs) | 3 | 3 | Phases avec critères d'acceptation ; premier portefeuille de connecteurs à choisir | Ouvert : décision métier attendue |
| R13 | Dépendance à un fournisseur d'IA | 2 | 2 | Couche d'abstraction, budgets par organisation | Phase 4 |
| R14 | Perte de données | 1 | 3 | Volumes persistants, `pg_dump` quotidien chiffré hors serveur, restauration testée | Procédure écrite ; test automatisé en phase 7 |

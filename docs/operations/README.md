# Exploitation et dépannage

## Santé

| Point | Rôle |
|---|---|
| `GET /health/live` | Le processus répond |
| `GET /health/ready` | Base joignable **et** rôle applicatif sûr (ni superutilisateur, ni BYPASSRLS, ni propriétaire des tables). Répond `503` sinon. |

Les conteneurs `api` et `web` déclarent un `HEALTHCHECK` ; `docker compose ps` affiche leur état.

## Journaux

L'API écrit une ligne JSON par requête sur la sortie standard : `ts`, `level`, `request_id`, `method`, `path`, `status`, `duration_ms`. Chaque réponse porte l'en-tête `X-Request-Id`, à communiquer en cas d'incident. Aucun mot de passe, jeton ou cookie n'est journalisé.

```bash
docker compose logs -f api | jq 'select(.status >= 500)'
```

Caddy journalise en JSON sur sa sortie standard.

## Problèmes fréquents

| Symptôme | Cause probable | Action |
|---|---|---|
| `api` reste « unhealthy », `/health/ready` renvoie `503` | Mauvaise URL de base, ou API connectée avec le rôle propriétaire ou superutilisateur | Vérifier `secrets/database_url` : l'utilisateur doit être `inteylo_app`. Journal : `unsafe database role` |
| `migrate` échoue au premier démarrage | Volume `pgdata` initialisé avant l'ajout du script `01-roles.sh` (les scripts d'init ne s'exécutent qu'une fois) | Créer les rôles à la main avec le contenu de `infrastructure/postgres/init/01-roles.sh`, ou recréer le volume s'il ne contient rien |
| Toutes les requêtes modifiantes sont refusées « pour des raisons de sécurité » | En-tête `X-Inteylo-Client` absent (appel direct sans l'interface) | Ajouter l'en-tête `X-Inteylo-Client: <nom-du-client>` |
| Connexion impossible en local, sans message d'erreur | Cookie `Secure` sur `http://` | `INTEYLO_COOKIE_SECURE=false` en développement uniquement |
| L'interface affiche « Impossible de joindre le serveur » | `/api` non relayé | Production : vérifier Caddy. Développement : définir `API_INTERNAL_URL` **avant** `npm run build` ou `npm run dev` |
| « Trop de tentatives » à la connexion | Limiteur (10 essais / 15 min par couple IP + e-mail) | Attendre la fin de la fenêtre ; le compteur est en mémoire, il se réinitialise au redémarrage de l'API |
| Certificat TLS non obtenu | DNS ne pointe pas vers le serveur ou port 80 fermé | Vérifier `dig $INTEYLO_DOMAIN` et le pare-feu ; journaux du conteneur `proxy` |

## Incidents de sécurité

1. **Compte compromis** : l'utilisateur ou un administrateur révoque les sessions (« Révoquer les autres sessions », ou désactivation du membre : effet immédiat).
2. **Organisation à isoler** : le super-administrateur la suspend depuis la console de plateforme ; toutes les requêtes vers cette organisation sont alors refusées.
3. **Investigation** : journal d'audit de l'organisation (interface ou table `audit_events`, en ajout seul), journaux HTTP corrélés par `request_id`.
4. **Secret de base exposé** : générer un nouveau mot de passe, puis `ALTER ROLE inteylo_app PASSWORD '...'`, mettre à jour `secrets/database_url` et redémarrer `api`.

## Dépannage de la CI

| Échec | Reproduction locale |
|---|---|
| Ruff ou mypy | `cd apps/api && ruff format . && ruff check . && mypy app` |
| Tests API | `INTEYLO_TEST_ADMIN_URL=... pytest -x -vv` |
| ESLint `i18next/no-literal-string` | Déplacer le texte vers `messages/fr.json` et utiliser `t("…")` |
| `i18n:check` | `npm run i18n:check` liste les clés manquantes, vides ou en anglais |
| Playwright | `npm run test:e2e`, puis `npx playwright show-report` |
| Trivy | `trivy image inteylo/api:<tag>` ; mettre à jour l'image de base ou la dépendance signalée |
| pip-audit, npm audit | Mettre à jour la dépendance, régénérer `requirements.lock` ou `package-lock.json` |

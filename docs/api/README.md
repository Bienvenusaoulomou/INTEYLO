# API INTEYLO

Contrat complet : `openapi.json` (généré depuis le code ; documentation interactive sur `/docs` en développement uniquement).

## Conventions

- Préfixe public : `/api` derrière le proxy ; l'API elle-même publie `/v1/...` et `/health/...`.
- Authentification : cookie de session `inteylo_session` (posé par `/v1/auth/login`, `/v1/auth/signup` ou `/v1/invitations/accept`).
- Requêtes modifiantes : en-tête `X-Inteylo-Client` obligatoire.
- Erreurs : toujours au format

```json
{ "error": { "code": "permission_denied", "message": "Vous n'avez pas l'autorisation d'effectuer cette action.", "details": [] } }
```

`code` est stable et documenté dans `contracts/identity.json`. `message` est toujours en français. Pour les erreurs de validation, `details` contient `{ "field": "...", "message": "..." }` en français.

## Points d'accès (phase 1)

| Méthode | Chemin | Permission |
|---|---|---|
| `POST` | `/v1/auth/signup` | publique |
| `POST` | `/v1/auth/login` | publique |
| `POST` | `/v1/auth/logout` | session |
| `GET` | `/v1/auth/me` | session |
| `GET` | `/v1/auth/sessions` | session |
| `DELETE` | `/v1/auth/sessions/{id}` | session (les siennes uniquement) |
| `POST` | `/v1/auth/sessions/revoke-others` | session |
| `GET` / `PATCH` | `/v1/orgs/{org_id}` | `organizations.read` / `organizations.manage` |
| `GET` | `/v1/orgs/{org_id}/roles` | `roles.read` |
| `GET` | `/v1/orgs/{org_id}/members` | `users.read` |
| `PUT` | `/v1/orgs/{org_id}/members/{id}/roles` | `roles.manage` + règles de délégation |
| `POST` | `/v1/orgs/{org_id}/members/{id}/disable` · `/enable` | `users.manage` + règles de délégation |
| `GET` / `POST` | `/v1/orgs/{org_id}/invitations` | `users.read` / `users.invite` |
| `DELETE` | `/v1/orgs/{org_id}/invitations/{id}` | `users.invite` |
| `GET` | `/v1/orgs/{org_id}/audit` | `audit.read` |
| `POST` | `/v1/invitations/inspect` · `/accept` | jeton d'invitation |
| `GET` | `/v1/platform/organizations` | `platform.organizations.read` |
| `POST` | `/v1/platform/organizations/{id}/suspend` · `/reactivate` | `platform.organizations.suspend` |
| `GET` | `/health/live` · `/health/ready` | publique |

Régénérer `openapi.json` après une modification :

```bash
cd apps/api && INTEYLO_DATABASE_URL=postgresql+psycopg://x:y@127.0.0.1:1/z INTEYLO_ENVIRONMENT=development \
  python -c "import json; from app.main import app; json.dump(app.openapi(), open('../../docs/api/openapi.json','w'), ensure_ascii=False, indent=2)"
```

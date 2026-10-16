# Contribuer à INTEYLO

## Branches et commits

- Branche principale protégée : `main`. Tout changement passe par une pull request avec une CI verte.
- Messages de commit en français, à l'impératif : `Ajoute la révocation des invitations`.
- Une pull request = un lot cohérent, avec ses tests et sa documentation.

## Règles non négociables

1. **Isolation.** Toute nouvelle table métier porte `org_id`, une politique RLS et un test d'isolation (ADR-0003).
2. **Autorisations côté serveur.** Chaque route déclare sa permission. L'interface ne fait que masquer, elle n'autorise rien.
3. **Audit.** Toute opération sensible et tout refus produisent un `AuditEvent`, sans secret dans `details`.
4. **Langue.** Aucun texte visible en dur : catalogue `fr` côté interface, `messages_fr.py` côté API. Un nouveau code d'erreur exige son message français et son entrée dans `contracts/identity.json`.
5. **Glossaire.** Rôles, modules et états utilisent les libellés de `docs/phase-0/07-glossaire.md`.
6. **Secrets.** Jamais dans le dépôt, les images, les journaux ni les jeux de test.
7. **Honnêteté.** Un connecteur ou une fonction simulée n'est jamais présenté comme réel ; l'inventaire `docs/connectors/inventaire.md` reflète l'état vérifié.

## Avant d'ouvrir une pull request

```bash
# API
cd apps/api && ruff format . && ruff check . && mypy app && pytest
# Interface
cd apps/web && npm run lint && npm run i18n:check && npm run typecheck && npm test
```

## Migrations

```bash
cd apps/api
alembic revision -m "description en français"
```

Les migrations sont écrites à la main (pas d'autogénération) et incluent les politiques RLS et les `GRANT` vers le rôle applicatif. Elles sont exécutées avec le rôle propriétaire, jamais avec celui de l'API.

## Décisions d'architecture

Toute décision structurante fait l'objet d'un ADR dans `docs/decisions/ADR-NNNN-titre.md` (contexte, décision, conséquences).

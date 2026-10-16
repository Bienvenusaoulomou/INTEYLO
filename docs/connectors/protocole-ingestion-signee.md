# Protocole d'ingestion signée — v1.1

Statut : spécification validée en phase 0 · implémentation prévue en phase 2 (B-22) · décision : ADR-0004.

Ce protocole s'applique à toute source qui **pousse** des données vers INTEYLO : webhooks génériques, agents d'export installés chez un client, systèmes internes. Les connecteurs qui **tirent** les données par API (OAuth) suivent l'interface du §7.4 du prompt maître.

## 1. Routes

Toutes les routes sont publiées sous `https://<domaine>/api` derrière le proxy.

| Méthode | Chemin | Rôle |
|---|---|---|
| `POST` | `/v1/ingest/{source_type}/deliveries` | Envoi d'un lot |
| `GET` | `/v1/ingest/{source_type}/deliveries/{delivery_id}` | État d'une livraison |
| `GET` | `/v1/ingest/{source_type}/ping` | Test de connexion et de signature |

`source_type` est une valeur du registre des connecteurs, par exemple `webhook_generic`.

## 2. En-têtes obligatoires

| En-tête | Contenu |
|---|---|
| `X-Inteylo-Connection` | Identifiant public de la connexion (`con_` + 26 caractères), créé dans le Centre des connecteurs |
| `X-Inteylo-Timestamp` | Secondes Unix |
| `X-Inteylo-Nonce` | 128 bits aléatoires, encodés en base64url |
| `X-Inteylo-Signature` | `v1=` + HMAC-SHA256 en hexadécimal |
| `Content-Type` | `application/json` (POST uniquement) |

## 3. Signature

```
chaine = METHODE + "\n"
       + CHEMIN_ET_QUERY + "\n"          # tel que reçu par l'API, ex. /v1/ingest/webhook_generic/ping
       + X-Inteylo-Connection + "\n"
       + X-Inteylo-Timestamp + "\n"
       + X-Inteylo-Nonce + "\n"
       + hex(SHA-256(corps brut))        # SHA-256 de la chaîne vide pour un GET
signature = hex(HMAC-SHA256(secret_de_la_connexion, chaine))
```

Ordre de vérification côté serveur :

1. Lire `X-Inteylo-Connection` et charger la connexion active et son secret. Si elle est inconnue ou désactivée : `401 ingest_signature_invalid`. La réponse est identique dans les deux cas, pour ne pas révéler quelles connexions existent.
2. Contrôler que l'horodatage est dans ± 300 s : sinon `401 ingest_timestamp_expired`.
3. Lire le corps **brut** (`await request.body()`), après avoir contrôlé `Content-Length` ≤ la limite configurée (1 Mo par défaut), sinon `413`.
4. Recalculer la signature et la comparer avec `hmac.compare_digest`.
5. Enregistrer le nonce, avec une contrainte d'unicité `(connexion, nonce)` conservée 10 minutes. Un nonce déjà vu donne `409 ingest_replay`.
6. Seulement ensuite, parser le JSON.

La rotation de secret accepte l'ancien et le nouveau secret pendant 24 h.

## 4. Corps d'un lot

```json
{
  "protocolVersion": "1.1",
  "deliveryId": "dlv_01JA...",
  "records": [
    {
      "type": "contact",
      "externalId": "c-1042",
      "operation": "upsert",
      "occurredAt": "2026-10-16T09:12:44Z",
      "sourceVersion": 7,
      "data": { "email": "client@example.com", "name": "…" },
      "fingerprint": "sha256:…"
    }
  ]
}
```

- `operation` vaut `upsert` ou `delete`.
- `fingerprint` = `sha256:` + hex(SHA-256(JCS(enregistrement sans le champ `fingerprint`))), où JCS désigne la canonicalisation RFC 8785.
- Les montants sont transmis en chaînes décimales avec un champ `currency` (ISO 4217). Les dates sont en ISO 8601 avec fuseau.

## 5. Règles de traitement

| Situation | Résultat |
|---|---|
| Signature, horodatage et nonce valides, `deliveryId` nouveau | `202 ACCEPTED`, puis `VERIFIED` une fois les enregistrements écrits **et relus** |
| Empreinte recalculée ≠ empreinte reçue | Enregistrement `REJECTED`, raison `fingerprint_mismatch` |
| `deliveryId` connu, même empreinte de lot | `200 DUPLICATE`, aucun effet |
| `deliveryId` connu, empreinte de lot différente | `409 REJECTED`, raison `payload_conflict`, événement d'audit |
| Un identifiant d'organisation présent dans `data` ne correspond pas au tenant de la connexion | `REJECTED`, raison `tenant_mismatch` |
| `occurredAt` ou `sourceVersion` plus ancien que l'état stocké | Conservé dans l'historique ; l'état courant n'est **pas** remplacé ; résultat `STALE` |
| `operation = delete` | Suppression logique du `SourceRecord`, propagée au modèle canonique, au graphe métier, aux index et à la mémoire ; auditée |
| Échec en cours d'écriture ou état inconnu | `UNCERTAIN` ; l'expéditeur interroge la route d'état avant tout renvoi |

L'empreinte d'un lot se calcule ainsi : SHA-256 de la concaténation ordonnée des empreintes de ses enregistrements.

## 6. Réponse (accusé)

```json
{
  "deliveryId": "dlv_01JA...",
  "status": "VERIFIED",
  "records": [
    { "externalId": "c-1042", "status": "VERIFIED", "fingerprint": "sha256:…" },
    { "externalId": "c-1043", "status": "REJECTED", "reason": "fingerprint_mismatch" }
  ]
}
```

L'empreinte renvoyée est celle que **INTEYLO a recalculée**. L'expéditeur la compare à la sienne : une égalité prouve que les mêmes octets canoniques ont été reçus.

## 7. Isolation

- La connexion détermine l'organisation : aucune valeur du corps ne peut la changer.
- La route d'état ne renvoie que les livraisons de la connexion signataire. Un `deliveryId` d'une autre connexion donne `404`, sans distinction possible avec un identifiant inexistant.
- Les tables `ingest_deliveries`, `ingest_nonces` et `source_records` portent `org_id` et la RLS (ADR-0003).

## 8. Tests requis (B-22)

Signature invalide · connexion inconnue · horodatage expiré (passé et futur) · rejeu de nonce · corps trop grand · doublon · conflit de contenu · empreinte falsifiée · tenant incohérent · livraison hors ordre · suppression propagée · accès croisé entre deux connexions de deux organisations · vecteurs de test JCS partagés entre Python et l'outil d'exemple de l'expéditeur.

# ADR-0004 — Protocole générique d'ingestion signée (abandon de Wix)

Statut : accepté · 16/10/2026

## Contexte

Le premier connecteur prévu était un site Wix poussant commandes, paiements et contacts. Le développement sur Wix est abandonné. Le protocole d'ingestion écrit pour lui contenait des règles solides (HMAC, idempotence, accusés avec empreinte, états `VERIFIED`/`UNCERTAIN`, isolation par locataire), mais aussi six défauts relevés à la revue.

## Décision

Ce protocole devient le contrat commun de **toutes** les sources qui poussent des données vers INTEYLO, sous le nom « protocole d'ingestion signée v1.1 » (`docs/connectors/protocole-ingestion-signee.md`). Les six défauts sont corrigés :

| Défaut de la v1 | Correction en v1.1 |
|---|---|
| Les `GET` ne permettaient pas de choisir le secret | En-tête `X-Inteylo-Connection` signé ; secret choisi avant toute lecture du corps |
| `JSON.stringify` non reproductible en Python | Empreinte sur la forme canonique JCS (RFC 8785), recalculée par INTEYLO |
| Signature d'un corps re-sérialisé | Signature du corps brut, comparaison en temps constant |
| Même `deliveryId` avec un contenu différent non défini | `REJECTED` + `payload_conflict`, journalisé |
| Livraisons hors ordre | Un enregistrement plus ancien n'écrase jamais un état plus récent |
| Suppressions non propagées | Propagation au modèle canonique, au graphe, aux index et à la mémoire |

Aucun code spécifique à Wix n'est conservé.

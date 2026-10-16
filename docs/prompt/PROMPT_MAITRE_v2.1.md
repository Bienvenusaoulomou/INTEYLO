# INTEYLO — PROMPT MAÎTRE DE DÉVELOPPEMENT MVP COMPLET
## Version 2.1 — Produit fonctionnel, intégrations, sécurité, Docker et CI/CD

**Destinataire : Claude Code ou agent de développement disposant d'un accès au dépôt et à un terminal.**

> Changements depuis la v2.0 (16/10/2026) :
> - Section 14 complétée : statut d'exigence bloquante, périmètre détaillé, formats via `Intl`, erreurs d'API, consigne de l'assistant, glossaire d'affichage rétabli.
> - Nouvelle section 7.7 : protocole générique d'ingestion signée (remplace le protocole Wix, abandonné).
> - Section 8 : livraisons hors ordre et propagation des suppressions.
> - Sections 17, 18, 20 et 21 : contrôles linguistiques détaillés, glossaire en Phase 0.
> - Section 22 rétablie : format des rapports de lot. La première action devient la section 23, avec la liste des livrables initiaux.

---

# 1. MISSION

Tu es une équipe senior de développement logiciel chargée de concevoir, coder, tester, sécuriser, documenter et préparer la publication d'INTEYLO.

Tu dois livrer un MVP réellement fonctionnel, pas une maquette, pas un simple dashboard, pas un prototype contenant des boutons inactifs et pas un ensemble de fichiers générés sans validation.

Tu dois travailler directement dans le dépôt disponible, examiner le code existant, créer les fichiers nécessaires, exécuter les commandes de développement, résoudre les erreurs et vérifier les résultats.

Tu ne dois jamais affirmer qu'un test passe, qu'un connecteur fonctionne, qu'une image a été publiée ou qu'un déploiement a réussi sans preuve obtenue pendant l'exécution.

Si tu disposes de plusieurs agents de développement, tu peux répartir le travail par modules, mais tu restes responsable de l'intégration, de la cohérence architecturale et de la validation finale.

## Objectif final

Livrer INTEYLO avec :

- Une application web complète et responsive.
- Une API backend fonctionnelle.
- Une authentification sécurisée.
- Un RBAC complet et une isolation multi-tenant.
- Un catalogue de connecteurs externes.
- Les connecteurs implémentés et testés selon les spécifications ci-dessous.
- Une ingestion et une normalisation des données.
- Un noyau analytique avec métriques et preuves.
- Un assistant métier qui utilise les données autorisées.
- Un moteur d'opportunités et d'anomalies.
- Une gestion contrôlée des actions.
- Un système d'approbation et de vérification des résultats.
- Une mémoire des décisions.
- Une interface entièrement en français.
- Des tests automatisés.
- Docker pour le développement et le déploiement.
- Une pipeline CI/CD avec contrôles DevSecOps.
- Une documentation complète.
- Des procédures de publication, de sauvegarde, de restauration et de dépannage.

Le MVP doit être publiable lorsque ses critères d'acceptation sont satisfaits. Les fonctionnalités dépendant de credentials externes, de contrats fournisseurs ou de services payants doivent être clairement identifiées et testées dans la mesure permise par les accès disponibles.

Ne simule jamais silencieusement une fonctionnalité manquante.

---

# 2. VISION DU PRODUIT

INTEYLO est une plateforme SaaS d'intelligence opérationnelle multi-tenant qui relie les données de plusieurs systèmes pour aider les organisations à comprendre leurs activités, prendre des décisions justifiées et exécuter des actions autorisées.

Le produit combine :

1. Un noyau de données commun.
2. Des connecteurs externes.
3. Des moteurs métier spécialisés.
4. Un moteur d'intelligence artificielle.
5. Un système d'exécution d'actions.
6. Une mémoire des décisions et de leurs résultats.
7. Un système d'audit et de sécurité.

L'ambition est de couvrir plusieurs domaines métier sans créer une application indépendante pour chaque domaine.

Le noyau commun doit permettre de connecter, normaliser, relier, analyser et exploiter les données de différents systèmes.

## Proposition de valeur

INTEYLO doit aider l'utilisateur à :

- Comprendre ce qui se passe dans son organisation.
- Identifier les évolutions et anomalies.
- Comprendre les causes probables d'un résultat.
- Retrouver les sources qui justifient une analyse.
- Comparer plusieurs scénarios.
- Déterminer les actions pertinentes.
- Faire approuver les actions sensibles.
- Exécuter les actions autorisées.
- Vérifier les résultats réels.
- Capitaliser sur les décisions précédentes.

Ne prétends pas que cette proposition de valeur est unique sur le marché. Construis un produit cohérent, mesurable et extensible.

---

# 3. RÈGLES DE DÉVELOPPEMENT

## 3.1 Travailler dans le dépôt réel

Commence par :

- Inspecter les fichiers et dossiers existants.
- Identifier le framework, les dépendances, les migrations et les tests existants.
- Examiner les fichiers Docker et CI/CD présents.
- Vérifier l'état Git.
- Détecter les fonctionnalités déjà implémentées.
- Identifier les erreurs et les risques.
- Conserver les éléments valides.
- Éviter de supprimer du code existant sans justification.

Si le dépôt est vide, crée une structure initiale cohérente.

Si des décisions antérieures existent dans la documentation (`docs/decisions/`), examine-les avant de les modifier. Toute décision d'architecture importante fait l'objet d'un ADR.

## 3.2 Exécution réelle

Pour chaque lot :

1. Définir les fonctionnalités.
2. Implémenter le code.
3. Exécuter les contrôles statiques.
4. Exécuter les tests.
5. Corriger les erreurs.
6. Vérifier l'intégration.
7. Mettre à jour la documentation.
8. Présenter les résultats observés (format de la section 22).

Ne fournis pas seulement des instructions destinées à l'utilisateur lorsque tu peux réellement exécuter le travail.

Ne remplace pas les tests par une affirmation selon laquelle le code devrait fonctionner.

## 3.3 Gestion des dépendances

Utilise des versions compatibles et maintenues.

Évite les dépendances inutiles, les bibliothèques abandonnées et les services coûteux sans justification.

Épingle les dépendances de manière reproductible et documente les décisions importantes.

---

# 4. STACK TECHNIQUE

Utilise cette stack comme choix de référence, sauf incompatibilité importante démontrée par l'inspection du dépôt.

## Frontend

- React.
- TypeScript.
- Next.js.
- Une bibliothèque de composants accessible et maintenue.
- Un client API typé.
- Une gestion d'état adaptée aux besoins réels.
- next-intl (ou équivalent justifié) pour le catalogue de traduction.
- Vitest pour les tests unitaires.
- Playwright pour les tests de bout en bout.

## Backend

- Python.
- FastAPI.
- Pydantic.
- SQLAlchemy.
- Alembic.
- Pytest.

## Données

- PostgreSQL comme base relationnelle principale.
- Redis uniquement si nécessaire pour le cache, les tâches ou la coordination.
- Un système de tâches asynchrones adapté à l'ingestion et aux workflows.
- Un stockage objet si des fichiers, exports ou documents doivent être conservés.

## Infrastructure

- Docker.
- Docker Compose.
- Reverse proxy HTTPS.
- GitHub Actions si le dépôt utilise GitHub ; Jenkins si l'environnement existant l'impose.
- Registre d'images comme GHCR ou équivalent.
- Outils de scan de sécurité.
- Logs structurés et monitoring.

Ne déploie pas systématiquement toutes les technologies de cette liste. Justifie chaque composant et évite la complexité prématurée.

---

# 5. ARCHITECTURE DU PRODUIT

Commence par un monolithe modulaire avec des workers asynchrones.

Ne crée pas une architecture microservices complexe pour un MVP si elle ne répond pas à un besoin démontré.

Organise le code autour des domaines suivants :

- identity
- organizations
- authorization
- connectors
- ingestion
- canonical_data
- business_graph
- metrics
- evidence
- analytics
- opportunities
- decision_simulator
- ai_assistant
- action_registry
- policy_engine
- approvals
- workflows
- execution_verifier
- decision_memory
- audit
- notifications
- billing, si nécessaire au modèle commercial initial.

Chaque module doit posséder des responsabilités clairement définies et des interfaces explicites.

Évite les dépendances circulaires.

Les opérations longues doivent être exécutées en arrière-plan plutôt que de bloquer les requêtes HTTP.

Fournis les diagrammes :

- `docs/architecture/use-case-diagram.puml`
- `docs/architecture/component-diagram.puml`
- `docs/architecture/domain-model.puml`
- `docs/architecture/action-sequence.puml`
- `docs/architecture/deployment-diagram.puml`
- `docs/architecture/logical-architecture.mmd`
- `docs/architecture/physical-architecture.mmd`

Les diagrammes doivent correspondre au code livré. Les libellés visibles des diagrammes destinés aux utilisateurs ou aux rapports sont en français (glossaire de la section 14).

---

# 6. RBAC ET MULTI-TENANCY

Le système doit être multi-tenant dès sa conception.

Chaque organisation possède ses utilisateurs, connexions, données, métriques, analyses, actions et mémoires.

## Rôles initiaux

### Platform Super Admin

Gère la plateforme globale, les organisations et les paramètres transversaux. L'accès aux données métier des clients doit être limité, justifié et audité.

### Organization Owner

Gère son organisation, ses membres, ses paramètres et ses connexions, selon les droits disponibles.

### Organization Admin

Administre les utilisateurs, les rôles délégués, les modules, les connecteurs et les politiques autorisées.

### Analyst

Consulte les données autorisées, lance des analyses, crée des rapports et prépare des recommandations.

### Operator

Exécute les opérations autorisées et suit leurs résultats.

### Viewer

Dispose d'un accès en lecture seule aux ressources explicitement partagées.

### Approver

N'est pas nécessairement un rôle indépendant : il s'agit d'une permission attribuée à un utilisateur autorisé à approuver certains types d'actions.

## Permissions atomiques

Prévois au minimum :

- `organizations.read`
- `organizations.manage`
- `users.read`
- `users.invite`
- `users.manage`
- `roles.read`
- `roles.manage`
- `connectors.read`
- `connectors.configure`
- `analytics.read`
- `analytics.run`
- `reports.create`
- `actions.propose`
- `actions.approve`
- `actions.execute`
- `memory.read`
- `memory.manage`
- `audit.read`
- `billing.manage`

Ajoute les permissions spécifiques requises par les modules. La liste est versionnée.

## Exigences

- Vérifier les permissions côté serveur.
- Refuser par défaut les opérations non autorisées.
- Vérifier le tenant à chaque accès à une ressource.
- Empêcher les accès inter-tenant, au niveau applicatif et, lorsque c'est approprié, au niveau de la base (Row-Level Security).
- Empêcher les utilisateurs de s'accorder eux-mêmes des privilèges.
- Empêcher un administrateur d'organisation de modifier les rôles globaux.
- Prévoir la révocation immédiate des accès.
- Protéger les sessions et les jetons.
- Journaliser les opérations privilégiées.
- Tester les tentatives d'élévation de privilèges.
- Appliquer des règles contextuelles supplémentaires aux actions sensibles.
- Ne jamais considérer la visibilité d'un bouton frontend comme une autorisation.

Les permissions doivent être testées dans les endpoints API, les workflows, les tâches asynchrones et les opérations des connecteurs.

---

# 7. CATALOGUE COMPLET DES CONNECTEURS

Le catalogue initial doit couvrir les familles suivantes :

1. CRM et ventes.
2. Marketing et publicité.
3. Réseaux sociaux.
4. Analytics et attribution.
5. Conversion et collecte d'événements.
6. Support et relation client.
7. Gestion de projet et collaboration.
8. Finance et facturation.
9. Stockage de fichiers et documents.
10. E-commerce.
11. Bases de données et entrepôts de données.
12. Webhooks et API personnalisées.
13. Import de fichiers.
14. Services d'intelligence artificielle.

Le catalogue est extensible. Ne limite pas l'architecture à une liste codée en dur.

## 7.1 Connecteurs prioritaires

Implémente les intégrations suivantes lorsque leurs API officielles sont accessibles et que les autorisations requises sont disponibles.

### CRM et ventes

- HubSpot.
- Salesforce.
- Pipedrive.

### Marketing et publicité

- Google Ads.
- Meta Ads.
- Google Analytics 4.
- Google Search Console.
- Mailchimp.

### Réseaux sociaux

- Facebook Pages.
- Instagram professionnel.
- LinkedIn, selon les produits et autorisations disponibles.
- YouTube Analytics.
- TikTok for Business, selon les autorisations disponibles.
- X, selon les accès API et les droits du compte.

### Support

- Zendesk.
- Intercom.

### Gestion de projet

- Jira.
- Trello.
- Asana.

### Finance et facturation

- Stripe.
- QuickBooks, selon disponibilité régionale et accès.
- Autres systèmes financiers ajoutés par adaptateurs documentés.

### Fichiers et collaboration

- Google Drive.
- Microsoft OneDrive ou SharePoint.
- Google Sheets.
- Microsoft Excel via les API disponibles.

### E-commerce

- Shopify.

### Données et infrastructure

- PostgreSQL.
- MySQL.
- Import CSV.
- Import JSON.
- Import Excel.
- Webhooks génériques (protocole de la section 7.7).
- API REST personnalisées.
- Connexions SQL en lecture seule lorsque c'est approprié.

### Intelligence artificielle

Créer une couche d'abstraction pour les fournisseurs de modèles d'IA, avec prise en charge des fournisseurs effectivement configurés et de leurs API officielles.

Ne suppose pas que tous les fournisseurs possèdent les mêmes capacités ou formats.

Wix ne fait plus partie du périmètre. Aucun code spécifique à Wix ne doit être produit.

## 7.2 Ne pas prétendre que tous les connecteurs sont opérationnels

La liste précédente est le catalogue cible du MVP. Le statut réel de chaque connecteur doit être suivi individuellement.

Pour chaque connecteur, afficher un état précis :

- Disponible à configurer.
- Configuration incomplète.
- Authentification requise.
- Connecté.
- Synchronisation en cours.
- Synchronisation réussie.
- Erreur de synchronisation.
- Autorisation expirée.
- Fonctionnalités limitées par le fournisseur.
- Désactivé.

Un connecteur ne peut être déclaré « connecté » qu'après une authentification valide et un test réel réussi.

Un connecteur ne peut être déclaré « synchronisé » qu'après un import réel confirmé.

Un adaptateur simulé ne doit jamais être présenté comme une intégration réelle.

## 7.3 Fiche technique obligatoire par connecteur

Chaque connecteur doit disposer d'une fiche contenant :

- Nom et catégorie.
- Documentation officielle.
- Fournisseur.
- Type d'authentification.
- Scopes ou permissions nécessaires.
- Variables de configuration.
- Endpoints réellement pris en charge.
- Opérations de lecture disponibles.
- Opérations d'écriture disponibles.
- Limites et quotas connus.
- Stratégie de pagination.
- Gestion des erreurs.
- Gestion des tokens expirés.
- Politique de synchronisation.
- Tests unitaires.
- Tests d'intégration.
- Statut de validation réelle.
- Limitations connues.

## 7.4 Architecture des connecteurs

Définis une interface commune, par exemple :

- `get_authorization_url`
- `exchange_authorization_code`
- `refresh_credentials`
- `validate_connection`
- `get_capabilities`
- `fetch_data`
- `normalize_data`
- `execute_action`, uniquement si pris en charge
- `verify_action`
- `disconnect`

Adapte cette interface aux différences réelles entre fournisseurs.

Chaque connecteur doit gérer les erreurs, les quotas, les délais d'attente, les tokens expirés et les reprises.

Ne force pas une abstraction identique lorsque les capacités des fournisseurs sont différentes.

## 7.5 Sécurité des connecteurs

- Chiffrer les secrets persistés.
- Ne jamais transmettre les secrets aux modèles d'IA.
- Ne jamais exposer les tokens dans le frontend.
- Appliquer le principe du moindre privilège.
- Vérifier les scopes avant les opérations.
- Journaliser les actions sans enregistrer les secrets.
- Protéger les endpoints OAuth contre les attaques CSRF.
- Valider les URL de redirection OAuth.
- Contrôler les destinations des webhooks.
- Protéger les connecteurs contre les risques SSRF.
- Limiter les connexions SQL et les requêtes personnalisées.
- Révoquer et supprimer les connexions de manière contrôlée.

## 7.6 Tests sans credentials

Lorsque les identifiants fournisseurs ne sont pas disponibles :

- Créer des tests unitaires avec des réponses HTTP simulées.
- Utiliser les fixtures et schémas documentés par le fournisseur.
- Tester les erreurs, quotas et tokens expirés.
- Ajouter des tests d'intégration réels exécutables lorsque les credentials sont disponibles.
- Documenter les variables nécessaires.
- Ne pas considérer les tests simulés comme une validation de l'API réelle.

## 7.7 Protocole générique d'ingestion signée

Toute source qui pousse des données vers INTEYLO (webhooks génériques, agents d'export, systèmes clients) utilise un protocole unique, documenté dans `docs/connectors/protocole-ingestion-signee.md`.

Routes :

- `POST /v1/ingest/{source_type}/deliveries` : envoi d'un lot.
- `GET /v1/ingest/{source_type}/deliveries/{delivery_id}` : état d'une livraison.
- `GET /v1/ingest/{source_type}/ping` : test de connexion.

Règles obligatoires :

1. **Identification avant vérification.** Chaque requête porte l'en-tête `X-Inteylo-Connection` (identifiant public de la connexion). INTEYLO choisit le secret HMAC d'après cet en-tête, jamais en lisant le corps avant vérification. L'en-tête fait partie de la chaîne signée.
2. **Signature sur le corps brut.** Chaîne signée : `méthode\nchemin+query\nX-Inteylo-Connection\nX-Inteylo-Timestamp\nSHA-256(corps brut)`. Le serveur lit les octets reçus (`await request.body()`), jamais un corps re-sérialisé. Comparaison en temps constant (`hmac.compare_digest`).
3. **Fenêtre temporelle.** Horodatage refusé au-delà de ± 300 secondes ; identifiant de requête (`X-Inteylo-Nonce`) mémorisé pendant la fenêtre pour bloquer le rejeu.
4. **Cohérence du locataire.** Après vérification, la connexion détermine le tenant. Tout `organization_id` ou identifiant d'instance présent dans le corps doit correspondre, sinon `REJECTED`. Les routes `GET` sont limitées à la connexion signataire : une connexion ne peut pas lire les livraisons d'une autre.
5. **Empreinte recalculée.** Chaque enregistrement porte une empreinte calculée sur sa forme canonique JCS (RFC 8785). INTEYLO **recalcule** l'empreinte et ne se contente jamais de renvoyer celle reçue ; une divergence donne `REJECTED` avec la raison `fingerprint_mismatch`.
6. **Idempotence.** Clé : `(connexion, delivery_id)`. Même identifiant et même empreinte : `DUPLICATE`. Même identifiant, empreinte différente : `REJECTED` avec la raison `payload_conflict`, enregistré dans l'audit.
7. **États.** `ACCEPTED` → `VERIFIED` (enregistré et relu) ou `UNCERTAIN` (état inconnu). L'expéditeur ne renvoie jamais un lot `UNCERTAIN` sans avoir interrogé la route d'état.
8. **Corps limité.** Taille maximale configurée, refus explicite au-delà.

---

# 8. INGESTION ET NORMALISATION

Construis une chaîne d'ingestion réutilisable par tous les connecteurs.

Elle doit prendre en charge :

- Synchronisation initiale.
- Synchronisation incrémentale si le fournisseur le permet.
- Pagination.
- Déduplication.
- Gestion des suppressions lorsque les API les exposent.
- Reprise après erreur.
- Historique des synchronisations.
- Versionnement des schémas.
- Contrôle de qualité.
- Traçabilité des données sources.
- Horodatage et fuseaux horaires.
- Gestion des devises.
- Gestion des données manquantes.
- Respect des quotas.

Règles d'ordre et de suppression :

- **Livraisons hors ordre.** Un enregistrement dont l'`occurred_at` (ou la version source) est plus ancien que celui déjà stocké ne remplace jamais l'état plus récent ; il est conservé dans l'historique.
- **Suppressions.** La suppression d'un enregistrement source (par exemple un contact) se propage au modèle canonique, au Business Graph, aux index de recherche et à la mémoire décisionnelle, selon les règles de conservation de la section 13. La propagation est tracée dans l'audit.

Le système doit distinguer :

- Les données originales.
- Les données normalisées.
- Les données calculées.
- Les prédictions.
- Les données dérivées par l'IA.

Chaque donnée normalisée doit pouvoir être reliée à sa source lorsque cela est possible.

Ne fusionne pas silencieusement deux clients, comptes ou organisations qui pourraient être distincts. Une commande créée, une commande payée et une conversion attribuée sont trois faits distincts.

---

# 9. MÉTRIQUES, PREUVES ET BUSINESS GRAPH

## Metric Registry

Permet de définir des indicateurs avec :

- Nom.
- Description.
- Formule.
- Unité.
- Devise éventuelle.
- Période.
- Source.
- Règles d'agrégation.
- Version.
- Date de validité.

## Evidence Engine

Les analyses importantes doivent pouvoir fournir :

- Les sources utilisées.
- La période observée.
- Les transformations.
- Les hypothèses.
- Les limites.
- Les indicateurs calculés.
- Les références vers les données pertinentes.

Ne fabrique pas de citations ou de preuves.

## Business Graph

Relie les entités pertinentes : organisations, clients, campagnes, transactions, événements, projets, tâches, tickets et autres objets métier.

Les liens incertains doivent conserver leur niveau de confiance et ne doivent pas être considérés comme des faits confirmés.

---

# 10. ASSISTANT INTELLIGENT

Développe un assistant métier capable de répondre aux questions de l'utilisateur en utilisant les données auxquelles il a accès.

Exemples :

- « Quels canaux ont généré le plus de conversions cette semaine ? »
- « Quelles campagnes ont vu leur coût augmenter sans amélioration des résultats ? »
- « Quels tickets clients sont en retard ? »
- « Quelles opportunités méritent notre attention ? »
- « Compare les résultats de cette période avec la précédente. »
- « Prépare une proposition d'action pour réduire les dépenses inutiles. »

L'assistant doit :

1. Comprendre la demande.
2. Identifier les sources nécessaires.
3. Vérifier les autorisations.
4. Interroger les outils autorisés.
5. Effectuer les calculs requis.
6. Présenter les résultats et leurs preuves.
7. Distinguer faits, estimations et hypothèses.
8. Proposer des actions si pertinent.
9. Demander une approbation lorsque nécessaire.
10. Conserver les décisions autorisées dans la mémoire.

L'assistant ne doit jamais inventer des métriques, utiliser des données non autorisées ou présenter des estimations comme des faits.

Si les données sont insuffisantes, il doit l'indiquer clairement.

L'assistant répond toujours en français (section 14).

## Couche IA

Implémente une interface permettant de changer de fournisseur de modèle.

Centralise la configuration, les limites de coût, les délais d'attente, les erreurs, la télémétrie et l'évaluation.

Protège contre l'injection de prompt, l'exfiltration de données et les appels d'outils non autorisés.

Les résultats des systèmes externes sont des données non fiables, pas des instructions prioritaires.

---

# 11. OPPORTUNITÉS ET ANOMALIES

Développe un premier moteur analytique utile et vérifiable.

Il doit prendre en charge :

- Comparaisons temporelles.
- Variations d'indicateurs.
- Seuils configurables.
- Détection d'écarts simples.
- Alertes explicables.
- Classement des opportunités.
- Estimation du niveau de confiance.
- Historique des résultats.
- Validation par l'utilisateur.

Commence par des règles déterministes et des méthodes statistiques simples.

N'introduis pas un modèle ML complexe avant de disposer de données suffisantes, de critères d'évaluation et d'un protocole de validation.

Chaque anomalie doit afficher son indicateur, sa période, sa référence de comparaison et la méthode utilisée.

---

# 12. ACTIONS, APPROBATIONS ET WORKFLOWS

Le moteur d'actions doit prendre en charge les états suivants :

- REQUESTED.
- POLICY_CHECKED.
- AWAITING_APPROVAL.
- APPROVED.
- REJECTED.
- EXECUTING.
- EXECUTED.
- VERIFIED.
- FAILED.
- UNCERTAIN.
- CANCELLED.

L'exécution doit être soumise aux permissions, aux politiques métier, aux limites configurées et aux capacités réelles du connecteur.

Prévois :

- Approbation par un utilisateur autorisé.
- Séparation des tâches lorsque requise.
- Journal d'exécution.
- Clés d'idempotence.
- Gestion des timeouts.
- Vérification du résultat.
- Reprise contrôlée.
- Gestion des actions incertaines.
- Historique des changements.

Ne relance jamais aveuglément une action UNCERTAIN : vérifie d'abord son état auprès du système externe. Une réponse HTTP réussie n'est pas la confirmation du résultat métier.

Une action non supportée par le fournisseur doit être clairement indiquée comme indisponible.

Une suggestion de l'IA ne constitue jamais une approbation.

---

# 13. MÉMOIRE DES DÉCISIONS

Enregistre les décisions autorisées avec :

- Contexte.
- Objectif.
- Sources.
- Hypothèses.
- Options examinées.
- Décision retenue.
- Approbateur éventuel.
- Action exécutée.
- Résultat observé.
- Date.
- Organisation propriétaire.
- Niveau de confiance.
- Version et provenance.

La mémoire doit distinguer les faits des interprétations.

Elle doit respecter les permissions d'accès, les règles de conservation, la correction des informations et la suppression autorisée (y compris la propagation des suppressions de la section 8).

Ne réutilise jamais la mémoire d'une organisation pour en informer une autre.

---

# 14. INTERFACE UTILISATEUR EN FRANÇAIS

Cette règle est une exigence fonctionnelle et un critère bloquant de qualité, non une simple préférence.

Tout ce qu'un utilisateur voit dans INTEYLO est en français. Aucun texte anglais ne doit être visible.

## 14.1 Périmètre

- Navigation, libellés, boutons, titres, placeholders, infobulles, états vides, messages de confirmation.
- Formulaires, validations et messages d'erreur, y compris ceux renvoyés par l'API et affichés à l'utilisateur.
- Tableaux, états, notifications, e-mails, rapports et exports CSV/PDF (en-têtes de colonnes compris).
- Réponses de l'assistant IA, même lorsque les données sources sont en anglais.
- Métadonnées des pages (`<title>`, description), textes alternatifs et `aria-label`.
- Noms des rôles, des modules et des états d'action : exclusivement selon le glossaire de la section 14.5.

Exception : les données des clients (noms de produits, contenus importés, champs des systèmes externes) sont affichées telles quelles et ne sont jamais traduites silencieusement.

## 14.2 Format et typographie

- `<html lang="fr">`. Français uniquement au lancement, sans sélecteur de langue. L'architecture (catalogue de traduction, aucune chaîne en dur) doit permettre d'ajouter d'autres langues plus tard sans réécrire les composants.
- Dates, heures, nombres et montants formatés via `Intl`, selon les paramètres régionaux de l'organisation, avec `fr` par défaut (JJ/MM/AAAA, 24 h, `1 234,56`). Affichage dans le fuseau horaire de l'organisation.
- La devise affichée est toujours celle de la donnée, jamais une devise imposée par défaut.
- Typographie française : espace insécable avant `: ; ? !`, guillemets « ».

## 14.3 Mise en œuvre

- Aucune chaîne visible en dur dans les composants : tous les textes proviennent du catalogue `fr`.
- Configurer en français les composants tiers : sélecteurs de dates, tableaux, bibliothèque d'authentification.
- L'API renvoie un `code` d'erreur stable, lisible par la machine, et un `message` en français. Les erreurs de validation Pydantic sont traduites à la frontière de l'API et ne sont jamais renvoyées brutes.
- La consigne système de l'assistant IA impose des réponses en français et l'usage du glossaire.
- Les identifiants techniques internes (code, variables, tables, enums, permissions comme `users.read`, clés de traduction) restent en anglais.
- Ne jamais afficher une clé de traduction, un identifiant technique, un nom de classe ou une valeur interne brute.

## 14.4 Contrôles bloquants en CI

- Règle de lint interdisant les chaînes littérales dans le JSX (`eslint-plugin-i18next` ou équivalent).
- Vérification que chaque clé utilisée existe dans le catalogue `fr`, sans traduction vide ni valeur de secours anglaise.
- Vérification que les messages d'erreur de l'API existent en français pour chaque code.
- Tests Playwright sur les pages principales, les erreurs et les états vides, vérifiant l'absence de clés non traduites et de texte anglais.

## 14.5 Glossaire d'affichage (interne → interface)

| Interne | Affiché |
|---|---|
| Platform Super Admin | Super-administrateur de la plateforme |
| Organization Owner | Propriétaire de l'organisation |
| Organization Admin | Administrateur de l'organisation |
| Analyst | Analyste |
| Operator | Opérateur |
| Viewer | Lecteur |
| Approver | Approbateur |
| REQUESTED / POLICY_CHECKED | Demandée / Contrôlée |
| AWAITING_APPROVAL / APPROVED | En attente d'approbation / Approuvée |
| EXECUTING / EXECUTED / VERIFIED | En cours / Exécutée / Vérifiée |
| FAILED / REJECTED / CANCELLED | Échouée / Refusée / Annulée |
| UNCERTAIN | Résultat incertain |
| Workspace / Dashboard | Espace de travail / Tableau de bord |
| Connector Hub | Centre des connecteurs |
| Business Graph | Graphe métier |
| Metric Registry | Référentiel des indicateurs |
| Evidence Engine | Preuves et sources |
| Opportunity Radar | Radar d'opportunités |
| Decision Simulator | Simulateur de décisions |
| Action Engine / Approval Center | Actions / Centre d'approbation |
| Decision Memory | Mémoire décisionnelle |
| Audit & Incident Center | Audit et incidents |
| Marketing Intelligence | Marketing |
| Social Hub | Réseaux sociaux |
| Conversion Intelligence | Conversions |
| CRM & Sales | Ventes et relation client |
| Support Intelligence | Support client |
| Project & Operations | Projets et opérations |
| Finance & Billing | Finance et facturation |
| Predictive Intelligence | Prévisions |
| Insight | Constat |
| Workflow | Processus |

## 14.6 Écrans obligatoires

- Connexion.
- Réinitialisation du mot de passe.
- Inscription ou invitation selon la politique choisie.
- Tableau de bord.
- Organisations et paramètres.
- Membres, rôles et permissions.
- Catalogue des connecteurs.
- Configuration d'un connecteur.
- État des synchronisations.
- Explorateur de données.
- Métriques et rapports.
- Assistant intelligent.
- Opportunités et anomalies.
- Plans d'action.
- Centre d'approbation.
- Historique des exécutions.
- Mémoire des décisions.
- Audit et incidents.
- Paramètres du compte.

Ne crée pas de boutons sans comportement. Chaque contrôle visible doit être connecté à une fonctionnalité réelle ou être explicitement désactivé avec une explication en français.

---

# 15. MODÈLE DE DONNÉES

Prévois au minimum les entités suivantes, adaptées aux besoins réels :

- Organization.
- User.
- Membership.
- Role.
- Permission.
- UserRole.
- RolePermission.
- Session ou RefreshToken.
- Connection.
- ConnectorCredentialReference.
- ConnectorCapability.
- SyncJob.
- SyncRun.
- IngestDelivery.
- SourceRecord.
- CanonicalEntity.
- EntityLink.
- MetricDefinition.
- MetricObservation.
- EvidenceReference.
- Insight.
- Decision.
- ActionPlan.
- ActionExecution.
- Approval.
- Workflow.
- MemoryEntry.
- AuditEvent.
- Notification.
- UsageRecord, si la facturation est activée.

Toutes les entités métier doivent être rattachées au bon tenant.

Ajoute les contraintes d'intégrité, les index, les migrations versionnées et les politiques de rétention appropriées.

N'enregistre pas de données personnelles ou de secrets inutiles.

---

# 16. DOCKER ET ENVIRONNEMENTS

Fournis :

- Dockerfiles du frontend, du backend et des workers.
- Docker Compose pour le développement.
- Configuration de test.
- Configuration de staging.
- Procédure de production.
- `.dockerignore`.
- `.env.example`.
- Health checks.
- Volumes persistants.
- Réseaux appropriés.
- Scripts de migrations.
- Scripts de tests.
- Procédures de sauvegarde et restauration.

Les conteneurs doivent fonctionner avec des privilèges minimaux (utilisateur non-root).

N'intègre aucun secret dans les images ou le dépôt.

N'expose pas publiquement les bases de données sans justification.

Documente les commandes exactes permettant de construire, démarrer, arrêter, tester et reconstruire l'application.

---

# 17. CI/CD ET DEVSECOPS

Choisis GitHub Actions ou Jenkins selon le dépôt et l'environnement réel. Ne maintiens pas deux pipelines concurrents sans besoin concret.

Le pipeline doit appliquer cet ordre général :

1. Checkout.
2. Formatage et lint.
3. Contrôle linguistique : chaînes visibles interdites hors catalogue, clés manquantes dans `fr`, traductions vides et valeurs de secours anglaises.
4. Vérification des types.
5. Tests unitaires.
6. Tests d'intégration.
7. Tests RBAC et multi-tenant.
8. Analyse statique du code.
9. Scan des secrets.
10. Scan des dépendances.
11. Build des images Docker.
12. Scan des images.
13. Publication des rapports.
14. Publication des images validées.
15. Déploiement staging.
16. Smoke tests.
17. Approbation de production lorsque requise.
18. Déploiement.
19. Vérification post-déploiement.
20. Procédure de rollback.

Outils possibles : Ruff, mypy, ESLint, Vitest, Playwright, Pytest, Semgrep, Gitleaks, OSV-Scanner, pip-audit et Trivy.

Ne conserve que les outils justifiés.

Les contrôles critiques, y compris les violations des règles linguistiques, doivent bloquer la publication en cas d'échec. Ne désactive pas un contrôle pour obtenir un pipeline vert ; toute exception est justifiée, limitée dans le temps et tracée.

Les secrets CI doivent être protégés et les permissions des workflows minimisées.

Les images doivent être versionnées et immuables. Le même artefact validé passe du staging à la production.

Ne déploie pas en production sans validation explicite des critères de mise en production et des autorisations nécessaires.

---

# 18. TESTS ET ACCEPTATION

Implémente :

- Tests unitaires.
- Tests d'intégration.
- Tests API.
- Tests d'autorisation.
- Tests inter-tenant.
- Tests des connecteurs.
- Tests de synchronisation.
- Tests des workflows.
- Tests de bout en bout.
- Tests de restauration.
- Tests de sécurité.
- Tests linguistiques.

Pour les connecteurs, distinguer les tests simulés des tests réels.

Tester les erreurs réseau, quotas, tokens expirés, doublons, timeouts, pagination, réponses malformées et reprises.

Pour le protocole d'ingestion signée, tester au minimum : signature invalide, horodatage expiré, rejeu, doublon, conflit d'empreinte, empreinte falsifiée et accès croisé entre connexions.

## Critères bloquants

- Aucun accès inter-tenant non autorisé dans les tests.
- Aucun chemin de contournement des permissions.
- Aucun secret exposé.
- Aucun texte anglais visible dans les interfaces, e-mails, exports ou réponses de l'assistant.
- Toutes les chaînes visibles proviennent du catalogue de traduction.
- Aucune clé de traduction obligatoire manquante, vide ou remplacée par une valeur anglaise.
- Formats de dates, d'heures, de nombres et de montants cohérents avec les paramètres régionaux configurés.
- Aucun bouton critique sans action fonctionnelle.
- Migrations reproductibles.
- Conteneurs démarrables et contrôles de santé fonctionnels.
- Pipeline CI reproductible.
- Actions sensibles auditées.
- Résultats analytiques justifiables.
- Statut réel des connecteurs affiché correctement.
- Documentation conforme au comportement livré.

Ne déclare pas le MVP prêt si des contrôles bloquants échouent.

---

# 19. DOCUMENTATION

Produis :

- `README.md`.
- `CONTRIBUTING.md`.
- `docs/architecture/`.
- `docs/connectors/`.
- `docs/security/`.
- `docs/api/`.
- `docs/deployment/`.
- `docs/testing/`.
- `docs/operations/`.
- `docs/decisions/`.
- `docs/release/`.

La documentation doit préciser :

- Installation.
- Configuration.
- Variables d'environnement.
- Gestion des secrets.
- Migrations.
- Commandes Docker.
- Tests.
- Configuration des connecteurs.
- Credentials requis.
- Scopes OAuth.
- Limites des API externes.
- Déploiement.
- Sauvegarde.
- Restauration.
- Monitoring.
- Dépannage.
- Procédure de publication.

Fournis un inventaire des connecteurs indiquant pour chacun les opérations réellement implémentées et le statut de validation.

---

# 20. MÉTHODE D'EXÉCUTION

Travaille par phases fonctionnelles.

## Phase 0 — Audit et conception

- Examiner le dépôt.
- Définir les exigences.
- Produire les diagrammes.
- Valider le RBAC.
- Définir le modèle de données.
- Établir le catalogue des connecteurs.
- Établir le glossaire d'affichage et le catalogue `fr` initial.
- Définir le plan de tests et le backlog.

## Phase 1 — Fondations sécurisées

- Structure du projet.
- Docker.
- Base de données.
- Authentification.
- Multi-tenancy.
- RBAC.
- Audit.
- Localisation française : catalogue `fr`, formats de dates et de montants, règles de lint associées.
- CI initiale.

## Phase 2 — Framework des connecteurs

- Interface commune.
- Registre des connecteurs.
- OAuth et secrets.
- Protocole d'ingestion signée (section 7.7).
- Synchronisation.
- Historique des jobs.
- Gestion des erreurs.
- Import CSV, JSON et Excel.
- Webhooks génériques.
- API REST personnalisées.

## Phase 3 — Connecteurs prioritaires

Implémenter les connecteurs métier selon la liste et les priorités définies.

Chaque connecteur doit être testé individuellement, documenté et intégré au pipeline.

## Phase 4 — Données et intelligence

- Modèle canonique.
- Business Graph.
- Métriques.
- Evidence Engine.
- Assistant intelligent.
- Opportunités et anomalies.

## Phase 5 — Actions et mémoire

- Policy Engine.
- Approbations.
- Workflow Orchestrator.
- Exécution.
- Vérification.
- Decision Memory.

## Phase 6 — Interface complète

- Tous les écrans requis.
- États de chargement.
- États vides.
- Erreurs.
- Responsive design.
- Accessibilité.
- Catalogue français.
- Tests de bout en bout.

## Phase 7 — Préproduction

- Suite de tests complète.
- Scans de sécurité.
- Build reproductible.
- Déploiement staging.
- Smoke tests.
- Sauvegardes et restauration.
- Documentation opérationnelle.

## Phase 8 — Publication

- Vérification de tous les critères.
- Rapport des limitations restantes.
- Images Docker publiées dans le registre autorisé.
- Configuration de production.
- Procédure de déploiement.
- Procédure de rollback.
- Checklist de publication.

Ne marque une phase comme terminée que lorsque ses critères d'acceptation sont vérifiés.

---

# 21. LIVRABLES ATTENDUS

À la fin, fournir :

1. Code source fonctionnel.
2. Frontend et backend intégrés.
3. Modèle de données et migrations.
4. RBAC et isolation multi-tenant.
5. Catalogue et implémentations des connecteurs.
6. Rapports de tests réels.
7. Diagrammes UML et architectures.
8. Fichiers Docker.
9. Pipeline CI/CD.
10. Rapports de sécurité.
11. Catalogue de traduction français et glossaire d'affichage.
12. Documentation complète.
13. Procédure de déploiement.
14. Procédure de sauvegarde et restauration.
15. Inventaire des connecteurs et de leurs capacités.
16. Liste des variables d'environnement nécessaires.
17. Liste des limitations restantes.
18. Checklist de publication.
19. Rapport final des critères satisfaits et non satisfaits.

Ne déclare pas les connecteurs nécessitant des identifiants externes validés en production si les tests réels n'ont pas pu être exécutés.

---

# 22. FORMAT DES RAPPORTS DE LOT

Pour chaque lot de développement, indique :

1. Objectif et périmètre.
2. Décisions d'architecture.
3. Fichiers créés ou modifiés.
4. Commandes exécutées.
5. Résultats réels des tests.
6. Problèmes détectés.
7. Risques et limites restantes.
8. Étapes suivantes.

Sépare clairement les éléments terminés, en cours, simulés et non implémentés.

Ne réécris pas inutilement des parties validées. Ne remplace pas une intégration réelle par un mock sans l'indiquer.

---

# 23. PREMIÈRE ACTION IMMÉDIATE

Commence maintenant par inspecter le dépôt et l'environnement.

Ne te limite pas à produire un plan.

Fournis d'abord un court diagnostic, puis commence la Phase 0 et crée les premiers livrables réels dans le dépôt :

1. Une analyse de l'état du projet.
2. L'architecture logique et physique documentée.
3. Le diagramme UML de cas d'utilisation.
4. Le modèle de données initial.
5. La matrice RBAC.
6. Le plan Docker et CI/CD.
7. Les risques techniques et de sécurité.
8. Un backlog ordonné avec critères d'acceptation.
9. Une décision motivée sur la stack.
10. La liste des livrables de la Phase 1.
11. Le catalogue de traduction `fr` initial.
12. Le glossaire d'affichage validé (rôles, modules, états d'action).

Après validation de la conception, passe à la Phase 1 et développe la première tranche fonctionnelle complète.

Ne t'arrête pas après la création du README, des diagrammes ou de la structure des dossiers.

Continue jusqu'à ce que le périmètre MVP soit implémenté, testé et documenté, en signalant clairement toute dépendance externe empêchant une validation réelle.

Lorsque tu rencontres un blocage, recherche une solution, teste-la et documente le résultat. Demande mon intervention uniquement lorsqu'une décision métier, un secret, un compte externe, un achat ou une autorisation explicite est réellement nécessaire.

**Résultat attendu : INTEYLO doit être un produit fonctionnel, cohérent, sécurisé, testable et prêt à être publié dès que les critères de mise en production sont satisfaits.**

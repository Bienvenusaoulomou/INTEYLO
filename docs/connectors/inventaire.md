# Inventaire des connecteurs

Mis à jour : 16/10/2026 (fin de phase 1).

**Aucun connecteur n'est implémenté à ce jour.** Le framework des connecteurs relève de la phase 2. Ce tableau sera tenu à jour connecteur par connecteur ; un connecteur n'y passe à « Validé (réel) » qu'après une authentification et une synchronisation réelles réussies.

Légende des statuts de développement : ⬜ non commencé · 🟡 en cours · 🧪 testé avec réponses simulées uniquement · ✅ validé contre l'API réelle.

| Famille | Connecteur | Authentification attendue | Statut | Prérequis externes |
|---|---|---|---|---|
| Ingestion | Webhooks génériques (protocole signé v1.1) | HMAC par connexion | ⬜ (spécifié) | aucun |
| Import | CSV, JSON, Excel | — | ⬜ | aucun |
| Données | API REST personnalisée | clé API ou OAuth | ⬜ | — |
| Données | PostgreSQL, MySQL (lecture seule) | identifiants SQL | ⬜ | base de test |
| CRM | HubSpot | OAuth 2 | ⬜ | compte développeur HubSpot |
| CRM | Salesforce | OAuth 2 | ⬜ | Developer Edition |
| CRM | Pipedrive | OAuth 2 | ⬜ | compte sandbox |
| Publicité | Google Ads | OAuth 2 + developer token | ⬜ | jeton développeur approuvé par Google |
| Publicité | Meta Ads | OAuth 2 (app Meta) | ⬜ | app Meta revue |
| Analytics | Google Analytics 4 | OAuth 2 | ⬜ | projet Google Cloud |
| Analytics | Google Search Console | OAuth 2 | ⬜ | propriété vérifiée |
| E-mailing | Mailchimp | OAuth 2 | ⬜ | compte |
| Social | Facebook Pages, Instagram professionnel | OAuth 2 (app Meta) | ⬜ | revue d'app Meta |
| Social | LinkedIn | OAuth 2 | ⬜ | produits LinkedIn approuvés |
| Social | YouTube Analytics | OAuth 2 | ⬜ | projet Google Cloud |
| Social | TikTok for Business | OAuth 2 | ⬜ | accès API accordé |
| Social | X | OAuth 2 | ⬜ | niveau d'accès API payant |
| Support | Zendesk, Intercom | OAuth 2 | ⬜ | comptes d'essai |
| Projets | Jira, Trello, Asana | OAuth 2 | ⬜ | comptes |
| Finance | Stripe | clé restreinte ou Stripe Connect | ⬜ | compte Stripe (mode test suffisant) |
| Finance | QuickBooks | OAuth 2 | ⬜ | sandbox Intuit, disponibilité régionale |
| Fichiers | Google Drive, Google Sheets | OAuth 2 | ⬜ | projet Google Cloud |
| Fichiers | OneDrive, SharePoint, Excel | OAuth 2 (Microsoft Entra) | ⬜ | inscription d'application Entra |
| E-commerce | Shopify | OAuth 2 (app) | ⬜ | compte Partner + boutique de développement |
| IA | Couche d'abstraction des modèles | clé API | ⬜ | fournisseur et budget à choisir |

Wix est retiré du périmètre (ADR-0004).

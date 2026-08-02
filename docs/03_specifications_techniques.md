# Spécifications Techniques — O-Suivi

> **Version** : 2.0  
> **Date** : 2026-07-23  
> **Auteur** : Renaud d'Harreville  
> **Statut** : Brouillon  
> **Pré-requis** : [Cahier des charges fonctionnel v1.5](01_cahier_des_charges_fonctionnel.md)

---

## 1. Synthèse des choix techniques

| Aspect | Choix | Justification |
|---|---|---|
| **Type d'application** | PWA (Progressive Web App) | Accessibilité universelle, pas d'installation, offline |
| **Frontend** | Vue.js 3 + Vite | Connu, léger, écosystème PWA mature |
| **Backend** | Python / FastAPI | Connu, performant, async natif |
| **Stockage** | Fichiers JSON | Simple, pas de serveur DB, facile à débugger |
| **Hébergement** | Google Cloud Platform (GCP) | Scalable, fiable |
| **Conteneurisation** | Docker | Déploiement reproductible |
| **Temps réel** | WebSocket (encadrants) | Réactivité du suivi en direct |
| **Authentification** | JWT 12h (encadrants) | Sécurité sans friction |
| **Offline** | Service Worker + IndexedDB | Données locales, sync au retour réseau |

---

## 2. Architecture globale

```
┌─────────────┐  HTTPS    ┌───────────────────┐         ┌──────────────┐
│  Frontend   │◀─────────▶│    Backend API    │◀───────▶│  Stockage    │
│  (PWA)      │  REST +   │    (FastAPI)      │         │  (JSON files)│
│  Vue.js 3   │  WebSocket│                   │         └──────────────┘
└─────────────┘           └───────────────────┘
      │                          │
      │ Service Worker           │ Docker
      │ + IndexedDB              │ (conteneur)
      ▼                          ▼
┌──────────────┐          ┌───────────────────┐
│  Cache local │          │   GCP             │
│  (offline)   │          │   Cloud Run / GCE │
└──────────────┘          └───────────────────┘
```

### 2.1 Flux de données principal


**Encadrant — suivi en direct :**
- Connexion WebSocket à l'ouverture de la vue Suivi ou Départ
- Le serveur envoie un signal "refresh" quand un log est écrit → le frontend re-fetch `/tracking` (full state)
- **Reconnexion automatique** : backoff exponentiel (1s → 2s → 4s → … → 30s max)
- **Sensible à la visibilité** : si la page est en arrière-plan (téléphone dans la poche), la reconnexion s'arrête. Elle reprend immédiatement quand la page redevient visible
- **Bandeau offline** : affiché quand la WebSocket est déconnectée, avec un bouton "Se reconnecter" pour forcer une tentative immédiate
- Pas de polling automatique en boucle

---

## 3. Frontend — PWA Vue.js

### 3.1 Stack détaillée

| Dépendance | Rôle | Version cible |
|---|---|---|
| `vue` | Framework UI | 3.x |
| `vite` | Build tool | 6.x |
| `vue-router` | Navigation SPA | 4.x |
| `pinia` | State management | 2.x |
| `vite-plugin-pwa` | Génération Service Worker (Workbox) | 0.20+ |
| `dexie` | Wrapper IndexedDB (stockage offline) | 4.x |

> 💡 Le client HTTP utilise l'API native `fetch` (pas de dépendance tierce comme axios ou ofetch).

### 3.2 Structure du projet frontend

```
frontend/
├── src/
│   ├── main.ts                    # Vue bootstrap + router
│   ├── App.vue                    # Root component (<router-view>)
│   ├── router/
│   │   └── index.ts               # Routes + auth guard
│   ├── stores/                    # Pinia stores
│   │   └── event-store.ts         # Store principal (événement, concurrents, tracking)
│   ├── types/                     # Types TypeScript
│   │   ├── event.ts               # Beacon, Course, TimeGateEntry, TimeGates
│   │   ├── competitor.ts          # CompetitorBeacon, TrackingCompetitor, DepartureCompetitor
│   │   └── log.ts                 # LogMetadata, LogEntry, BeaconInput
│   ├── utils/                     # Fonctions utilitaires pures
│   │   ├── date.ts                # Formatage dates (toLocalISO, formatTime, etc.)
│   │   └── competitor-state.ts    # Reconstruction d'état (buildCompetitorBeacons, etc.)
│   ├── composables/               # Composables Vue (logique réactive réutilisable)
│   │   ├── useAuth.ts             # Headers d'authentification
│   │   ├── useClock.ts            # Horloge temps réel
│   │   ├── useTimeGates.ts        # Logique PH (temps écoulé, statut, couleurs)
│   │   ├── useBeaconEdit.ts       # Édition inline des balises
│   │   ├── useCompetitorActions.ts # Actions suivi (abandon, tracker)
│   │   ├── useInlineEdit.ts       # Édition inline générique
│   │   ├── useDepartureActions.ts # Actions départ (départ, DNS, édition)
│   │   └── use-websocket.ts       # WebSocket (reconnexion auto, visibility-aware)
│   ├── components/
│   │   ├── CreateModal.vue        # Popup de création (champ nom)
│   │   ├── EventHeader.vue        # Header sticky partagé (Config/Départ/Suivi/Résultats)
│   │   └── suivi/                 # Sous-composants de la vue Suivi
│   └── views/
│       ├── LoginView.vue          # Page de connexion encadrant
│       ├── public/                # Vues publiques (sans auth)
│       │   ├── PublicResultsView.vue
│       │   └── PublicBeaconEditView.vue
│       └── admin/                 # Vues encadrants (auth requise)
│           ├── AdminHomeView.vue
│           ├── DepartView.vue
│           ├── SuiviView.vue
│           ├── ResultatsView.vue
│           ├── EventConfigView.vue
│           ├── TemplateConfigView.vue
│           ├── event-tabs/        # Onglets configuration événement
│           └── template-tabs/     # Onglets configuration template
├── vite.config.ts
├── package.json
└── index.html
```

### 3.3 PWA — Service Worker

**Plugin** : `vite-plugin-pwa` (Workbox, mode `generateSW`)

**Manifest** :
- `name` : "O-Suivi"
- `short_name` : "O-Suivi"
- `description` : "Suivi d'épreuves de course d'orientation"
- `theme_color` : `#1a1a2e` (couleur de marque, reprise de `variables.css`)
- `background_color` : `#ffffff`
- `display` : `standalone`
- `start_url` : `/`
- Icônes : `pwa-192x192.png`, `pwa-512x512.png` (dans `public/`)

**Stratégies de cache Workbox** :
- **Precache** : tous les assets statiques du build (JS, CSS, HTML, images) — gérés automatiquement par `generateSW`
- **Runtime — API** : `NetworkFirst` pour les requêtes `/api/` (renvoie le cache si le réseau échoue, TTL 24h)
- **Runtime — Icônes/polices** : `CacheFirst` (TTL 30 jours)

**Mise à jour du Service Worker** :
- Mode `prompt` : quand une nouvelle version est disponible, l'utilisateur est notifié et peut choisir de mettre à jour
- Composant `ReloadPrompt.vue` affiché si une mise à jour est disponible (bandeau "Nouvelle version disponible — Recharger")

**Contraintes réseau** :
- HTTPS obligatoire en production (requis par les navigateurs pour le Service Worker)
- En dev local : `http://localhost` est une exception autorisée

### 3.4 Stockage offline — IndexedDB (Dexie.js)

- **Actions offline** : file d'attente des actions non synchronisées (saisie balise, départ, modifications encadrant). Chaque action porte un horodatage local (ISO 8601).
- **Cache événement** : snapshot des données de l'événement en cours, mis à jour à chaque sync réussie.
- **Sync déclenchée** sur : retour en ligne, ouverture/focus de l'app, périodiquement (60s si en ligne).

### 3.5 Routing

```
/login                                      → Authentification encadrant
/admin                                      → Page d'accueil admin (onglets Templates + Événements)
/admin/templates/:id                        → Vue template (édition)
/admin/events/:id/config                    → Configuration événement
/admin/events/:id/depart                    → Vue départ
/admin/events/:id/suivi                     → Vue suivi
/admin/events/:id/resultats                 → Vue résultats

/events/:id                                 → Vue publique résultats (sans auth)
/events/:id/competitor/:userId/beacons      → Vue publique édition balises (sans auth)
```

---

## 4. Backend — FastAPI

### 4.1 Stack détaillée

| Dépendance | Rôle |
|---|---|
| `fastapi` | Framework API REST + WebSocket |
| `uvicorn` | Serveur ASGI |
| `pydantic` 2.x | Validation des données |
| `python-jose` ou `authlib` | JWT pour authentification |

> 💡 Stockage en fichiers JSON — pas de dépendances ORM/DB (pas de SQLAlchemy, Alembic, asyncpg).

### 4.2 Structure du projet backend

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entrypoint
│   ├── config.py                  # Settings (JWT, paths)
│   ├── dependencies.py            # Auth dependency (require_organizer)
│   ├── routers/                   # Endpoints groupés
│   │   ├── auth.py                # POST /api/auth/login
│   │   ├── templates.py           # CRUD templates + beacons/courses/time-gates
│   │   ├── events.py              # CRUD events + import-template + tracking
│   │   ├── registrations.py       # CRUD inscriptions + checkpoints
│   │   ├── logs.py                # Actions d'épreuve (encadrant, auth requise)
│   │   ├── results.py             # GET résultats (encadrant, auth requise)
│   │   ├── public.py              # Endpoints publics (sans auth)
│   │   └── ws.py                  # WebSocket (signal refresh)
│   ├── services/                  # Orchestration (coordonne repos + domain)
│   │   ├── results_service.py     # Calcul des résultats (orchestration)
│   │   ├── tracking_service.py    # Données de suivi agrégées
│   │   ├── checkpoint_service.py  # Récupération checkpoints d'un concurrent
│   │   ├── log_service.py         # Création/append de logs (partagé admin + public)
│   │   └── registration_service.py # CRUD inscriptions, déduplication, matching
│   ├── domain/                    # Logique métier pure
│   │   ├── exceptions.py          # Exceptions domaine (EntityNotFound)
│   │   ├── competitor_state.py    # CompetitorState + CheckpointEntry
│   │   ├── beacon_analyzer.py     # Analyse passages balises
│   │   ├── section_validator.py   # Validation sections PH
│   │   ├── results_calculator.py  # Logique métier résultats (validité, finish, tri)
│   │   └── time_utils.py          # Utilitaires temps
│   ├── repositories/              # Accès données (objets typés)
│   │   ├── event_repository.py
│   │   ├── template_repository.py
│   │   ├── log_repository.py
│   │   └── user_repository.py
│   ├── schemas/                   # Modèles Pydantic (DTOs, entités, unions)
│   │   ├── auth.py
│   │   ├── templates.py
│   │   ├── events.py
│   │   ├── registrations.py
│   │   ├── users.py
│   │   ├── results.py
│   │   ├── tracking.py
│   │   └── logs.py
│   └── websocket/
│       └── connection_manager.py  # Gestion connexions WS par événement
├── tests/
├── data/                          # Stockage JSON
├── Dockerfile
└── pyproject.toml
```

### 4.3 Endpoints principaux

**Niveaux d'accès** :
- **Admin** : JWT avec `role: "organizer"` requis (dépendance `require_organizer`)
- **Public** : aucune authentification (endpoints sous `/api/public/...` et vues publiques)
- **Login** : endpoint ouvert pour obtenir un JWT

#### Authentification

| Méthode | Endpoint | Accès | Description |
|---|---|---|---|
| POST | `/api/auth/login` | ouvert | Login encadrant (username + mot de passe) → JWT 12h |

#### Templates (admin)

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/api/templates` | Liste des templates |
| POST | `/api/templates` | Créer un template (nom) |
| GET | `/api/templates/{id}` | Détail d'un template (métadonnées : id, nom) |
| PATCH | `/api/templates/{id}` | Modifier le nom du template |
| GET | `/api/templates/{id}/beacons` | Lire le registre des balises |
| PUT | `/api/templates/{id}/beacons` | Remplacer le registre des balises |
| GET | `/api/templates/{id}/courses` | Lire les parcours (beacons enrichis) |
| PUT | `/api/templates/{id}/courses` | Remplacer les parcours (beacons par id) |
| GET | `/api/templates/{id}/time-gates` | Lire les temps PH |
| PUT | `/api/templates/{id}/time-gates` | Remplacer les temps PH |

> 💡 **Enrichissement des parcours** : `GET /courses` retourne les `courses[].beacons` sous forme d'objets complets (id, number, tag, is_ph) résolus depuis le registre. `PUT /courses` accepte les `courses[].beacons` sous forme de liste d'`id` (entiers) tels que stockés.

> 💡 **Endpoints par section** : chaque onglet de l'UI a ses propres GET/PUT. Le GET retourne la section, le PUT la remplace intégralement (pas de merge partiel).

#### Événements (admin)

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/api/events` | Liste des événements |
| POST | `/api/events` | Créer un événement (nom) |
| GET | `/api/events/{id}` | Détail complet d'un événement |
| PATCH | `/api/events/{id}` | Modifier un événement (merge partiel) |
| POST | `/api/events/{id}/import-template` | Importer beacons, courses et time_gates depuis le template sélectionné |
| GET | `/api/events/{id}/tracking` | Données de suivi agrégées (état complet de tous les concurrents pour les vues Départ et Suivi) |
| GET | `/api/events/{id}/resultats` | Résultats provisoires (tous les concurrents) |

> 💡 **Enrichissement des parcours** : même principe que pour les templates — les endpoints GET retournent les `courses[].beacons` enrichis, les endpoints PATCH acceptent des listes d'`id`.

#### Inscriptions (admin)

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `.../registrations` | Liste des inscrits (avec infos utilisateur) |
| POST | `.../registrations` | Inscrire un concurrent (crée le user si inexistant) |
| DELETE | `.../registrations/{uid}` | Désinscrire un concurrent |
| PUT | `.../registrations` | Remplacer toutes les inscriptions (import batch) |
| PATCH | `.../registrations/{uid}` | Modifier infos inscription (parcours, horaire, tracker…) |
| GET | `.../registrations/{uid}/checkpoints` | Checkpoints d'un concurrent (état courant reconstruit) |

> 💡 Le préfixe est `/api/events/{id}/registrations`. Le `uid` est l'identifiant de l'utilisateur (`user_id`).

> 💡 **`start_order`** n'est pas modifiable via `PATCH /registrations/{uid}`. L'ordre de départ est géré globalement via `PATCH /api/events/{id}` (qui remplace la liste complète des registrations, ordonnée).

#### Actions d'épreuve (admin — écrivent dans le log)

Chaque endpoint ci-dessous **ajoute une entrée** dans le log append-only du concurrent (voir [modèle de données §4](04_modele_de_donnees.md)).

| Méthode | Endpoint | Type log | Description |
|---|---|---|---|
| POST | `.../registrations/{uid}/depart` | `departure` | Confirmer le départ |
| POST | `.../registrations/{uid}/depart-cancel` | `departure_cancel` | Annuler le départ |
| POST | `.../registrations/{uid}/depart-edit` | `departure_edit` | Corriger l'heure de départ |
| POST | `.../registrations/{uid}/dns` | `dns` | Marquer absent (commentaire obligatoire) |
| POST | `.../registrations/{uid}/dns-cancel` | `dns_cancel` | Annuler le DNS (commentaire obligatoire) |
| POST | `.../registrations/{uid}/abandon` | `abandon` | Marquer abandon (commentaire obligatoire) |
| POST | `.../registrations/{uid}/abandon-cancel` | `abandon_cancel` | Annuler l'abandon (commentaire obligatoire) |
| POST | `.../registrations/{uid}/bag-weight` | `bag_weight` | Poids du sac (départ ou arrivée) |
| POST | `.../registrations/{uid}/tracker-returned` | `tracker_returned` | Tracker rendu (+ n° tracker) |
| POST | `.../registrations/{uid}/tracker-returned-cancel` | `tracker_returned_cancel` | Annuler le rendu tracker |
| POST | `.../registrations/{uid}/checkpoint-edit` | `checkpoint_edit` | Correction code balise (commentaire optionnel) |
| POST | `.../registrations/{uid}/ph-arrival-edit` | `ph_arrival_edit` | Corriger l'heure d'arrivée à une PH |
| GET | `.../registrations/{uid}/logs` | — | Historique complet des logs du concurrent |

> 💡 `GET /logs` n'est pas protégé par JWT (accessible sans auth). C'est intentionnel pour la phase de développement.

> 💡 L'`author_id` est **implicite** (déduit du JWT). Le client envoie `creation_date` (horloge locale, ISO 8601) et les `data` spécifiques au type. Le serveur ajoute `received_at` (horodatage serveur) pour traçabilité.

> 💡 **Distinction `creation_date` / `passage_time`** : `creation_date` (dans `metadata`) est l'horodatage de l'action elle-même. Pour les corrections (`checkpoint_edit`, `ph_arrival_edit`), le champ `passage_time` (dans `data`) est l'heure de passage corrigée — c'est une donnée métier, distincte de `creation_date`.

#### WebSocket

| Endpoint | Description |
|---|---|
| `ws://.../api/events/{id}/ws?token=...` | Flux temps réel pour les encadrants (signal "refresh" quand un log est écrit) |

#### Endpoints publics (aucune authentification)

Ces endpoints sont accessibles sans JWT. Ils servent la vue publique résultats + édition balises.

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/api/public/events/{id}/resultats` | Résultats provisoires (même réponse que `GET /api/events/{id}/resultats`) |
| GET | `/api/public/events/{id}/competitors/{uid}/checkpoints` | Checkpoints d'un concurrent (code + horaire, état reconstruit) |
| POST | `/api/public/events/{id}/competitors/{uid}/checkpoint-edit` | Édition d'une balise — `author_id = "public"` |
| POST | `/api/public/events/{id}/competitors/{uid}/ph-arrival-edit` | Correction heure d'arrivée PH — `author_id = "public"` |

> 💡 Les payloads des endpoints publics sont identiques à ceux des endpoints encadrant correspondants. La seule différence est l'`author_id` qui est fixé à `"public"` au lieu d'être déduit du JWT.

### 4.4 Authentification

**Encadrants :**
- Login **username + mot de passe** via `POST /api/auth/login`
- JWT signé (HS256), durée **12h**, contient : `{ user_id, role: "organizer", exp }`
- Réponse login : `{ token, role: "organizer" }`
- Stocké en localStorage
- Tous les encadrants = même rôle (admin)
- Les routers admin utilisent une dépendance `require_organizer` qui vérifie le rôle depuis le token et retourne 403 si le rôle n'est pas `organizer`

**Accès public :**
- Les endpoints sous `/api/public/...` ne nécessitent aucun JWT
- Les éditions publiques sont tracées avec `author_id = "public"` dans les logs

> 💡 Le frontend peut décoder le payload du JWT (base64) pour lire le rôle sans requête supplémentaire.

---

## 5. Stockage — Fichiers JSON

Le stockage repose sur des **fichiers JSON** (pas de base de données relationnelle).

**Justification :**
- Ultra-simple, pas de serveur DB à gérer
- Facile à débugger et inspecter (fichiers lisibles)
- Suffisant pour le volume de données (~50 concurrents, ~20 checkpoints par concurrent par événement)
- La concurrence d'écriture est gérée par le modèle append-only des logs

**Structure :** voir [04_modele_de_donnees.md](04_modele_de_donnees.md) pour le détail des fichiers.

> ⚠️ Pas de dépendances ORM (SQLAlchemy, Alembic, asyncpg). Le backend lit/écrit directement les fichiers JSON.

---

## 6. Stratégie offline détaillée

### 6.1 Matrice des fonctionnalités offline

| Fonctionnalité | Offline ? | Mécanisme |
|---|---|---|
| Confirmer départ (encadrant) | ✅ Oui | IndexedDB → sync |
| Modifier données concurrent (encadrant) | ✅ Oui | IndexedDB → sync |
| Vue suivi (encadrant) | ⚠️ Partiel | Dernières données connues en cache, pas de mise à jour temps réel |
| Création d'événement | ❌ Non | Opération préparatoire (faite en amont, avec réseau) |
| Vue résultats | ⚠️ Partiel | Derniers résultats cachés |

### 6.2 Résolution de conflits

**Principe : "`creation_date` wins" + actions idempotentes**

- Chaque action offline porte un **`creation_date`** (horloge du device, ISO 8601)
- Au moment de la sync, le serveur traite les actions dans l'**ordre chronologique** du `creation_date`
- Les actions sont **idempotentes** : renvoyer la même action 2 fois ne cause pas de doublon (déduplication par `creation_date + type + concurrent`)
- En cas de modifications concurrentes offline par deux encadrants, le `creation_date` le plus récent fait foi
- **L'historique complet** est conservé pour permettre aux encadrants de vérifier et corriger si nécessaire

### 6.3 Indicateur de statut réseau

L'application affiche en permanence :
- 🟢 **En ligne** — données synchronisées
- 🔴 **Hors-ligne** — N actions en attente de synchronisation + bouton "Synchroniser maintenant"
- 🔄 **Synchronisation en cours...**

---

## 7. Déploiement — GCP + Docker

### 7.1 Architecture de déploiement

```
┌──────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                 │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │              Cloud Run (ou GCE)                    │  │
│  │                                                    │  │
│  │   ┌──────────────────┐   ┌──────────────────────┐  │  │
│  │   │  Container       │   │  Container           │  │  │
│  │   │  Backend (API)   │   │  Frontend (Nginx)    │  │  │
│  │   │  FastAPI+Uvicorn │   │  Vue.js build static │  │  │
│  │   └──────────────────┘   └──────────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─────────────────────┐                                 │
│  │  Stockage           │                                 │
│  │  Fichiers JSON      │                                 │
│  │  (volume persistant)│                                 │
│  └─────────────────────┘                                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Option Cloud Run** (recommandée pour démarrer) :
- Serverless, pay-per-use, auto-scale
- Parfait pour un usage ponctuel (quelques probas par an)
- Pas de serveur à maintenir

> ⚠️ Cloud Run ne supporte pas nativement les WebSocket longue durée. Si WebSocket est retenu, prévoir Cloud Run avec "CPU always allocated" ou GCE.

**Option GCE** (si besoin de plus de contrôle) :
- VM avec Docker Compose
- Plus prévisible en coût si usage fréquent
- Compatible WebSocket sans restriction

### 7.2 HTTPS

- En production (GCP) : géré automatiquement par Cloud Run ou un Load Balancer
- **HTTPS obligatoire** pour que le Service Worker fonctionne
- En dev local : `http://localhost` est une exception autorisée

---

## 8. Sécurité

| Aspect | Mesure |
|---|---|
| Authentification encadrants | JWT signé (HS256), expiration 12h |
| Mots de passe | Stockés en clair (dev) — TODO: bcrypt avant production |
| Accès public | Endpoints `/api/public/...` sans JWT, éditions tracées avec `author_id = "public"` |
| HTTPS | Obligatoire en production |
| CORS | Configuré pour n'accepter que le domaine du frontend |
| Rate limiting | Sur les endpoints publics (anti-bruteforce login, anti-spam saisie) |
| Validation entrées | Pydantic (typage strict sur tous les endpoints) |

---

## 9. Environnement de développement

### 9.1 Pré-requis

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose

### 9.2 Structure monorepo

```
o-suivi/
├── frontend/        # Vue.js PWA
├── backend/         # FastAPI
├── docs/            # Documentation
├── agents.md        # Instructions pour agents IA
└── docker-compose.yml
```

---

## 10. Performance et limites

### 10.1 Dimensionnement cible

| Métrique | Valeur                                              |
|---|-----------------------------------------------------|
| Concurrents simultanés | 50 max                                              |
| Encadrants simultanés | 2-5                                                 |
| Connexions WebSocket simultanées | 2-5                                                 |
| Données par événement | ~1000 checkpoints max (50 concurrents × 20 balises) |

→ **Charge très faible**. Un seul conteneur Cloud Run (ou une petite VM) suffit largement.

### 10.2 Coûts estimés GCP

| Service | Estimation / mois |
|---|---|
| Cloud Run (backend) | ~0-5€ (quasi gratuit si usage ponctuel) |
| Stockage | Négligeable (fichiers JSON sur disque persistant) |
| Réseau | Négligeable |
| **Total** | **~0-5€/mois** (en période active), ~0€ en veille |

> 💡 Alternative économique : une instance `e2-micro` GCE (gratuite dans le free tier).

---

## 11. Questions ouvertes techniques

- [ ] Domaine final souhaité (pour la config HTTPS/CORS)
- [ ] Stratégie de backup des données (fichiers JSON)
- [ ] CI/CD : GitHub Actions pour build + deploy automatique ?
- [ ] Monitoring / alertes en production (logs, erreurs)
- [ ] Tests E2E : simuler un proba blanc complet avant le premier vrai événement ?
- [ ] WebSocket sur Cloud Run : valider la compatibilité ou basculer sur GCE

---

## 12. Prochaines étapes techniques

| # | Tâche | Priorité |
|---|---|---|
| 1 | Initialiser le repo (monorepo `frontend/` + `backend/`) | 🔴 Haute |
| 2 | Setup Docker Compose local | 🔴 Haute |
| 3 | Modèle de données (voir [04_modele_de_donnees.md](04_modele_de_donnees.md)) | 🔴 Haute |
| 4 | Endpoints API de base (CRUD événement, concurrents) | 🔴 Haute |
| 5 | Frontend : scaffold Vue.js + PWA + routing | 🔴 Haute |
| 6 | Authentification (JWT encadrants) | 🟡 Moyenne |
| 7 | Logique offline (IndexedDB + sync) | 🟡 Moyenne |
| 8 | WebSocket temps réel (vue suivi) | 🟡 Moyenne |
| 9 | Vues encadrants (départ, suivi, résultats) | 🟡 Moyenne |
| 10 | Déploiement GCP | 🟢 Basse (quand prêt) |
| 11 | Tests terrain (premier proba blanc réel) | 🟢 Basse |

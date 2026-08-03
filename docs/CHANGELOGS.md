# Changelog — O-Suivi

> Historique des modifications du projet.

---

## 2026-08-03

- **Page liste événements publics** : nouvelle vue `/events` accessible sans auth, listant tous les événements triés par date décroissante (frontend `PublicEventsListView.vue`, route, lien depuis login). Endpoint `GET /api/events` rendu public (auth retirée du router level, appliquée par endpoint sur les autres routes).
- **Offline Dexie.js** : IndexedDB via Dexie 4.x — file d'attente `pendingActions` (mutations POST/PATCH/PUT/DELETE enregistrées localement, replay séquentiel via endpoints individuels au retour réseau), cache `eventCache` (snapshots tracking et liste événements servis depuis IndexedDB quand le réseau échoue), sync engine avec triggers (online/visibility/60s/bouton), indicateur réseau global (🟢/🔴/🔄), composable `useOfflineStatus`, composant `OfflineIndicator.vue`, 21 nouveaux tests unitaires (db, cache-service, sync-engine)

---

## 2026-08-02

- **PWA** : `vite-plugin-pwa` configuré (mode `generateSW`, stratégie `prompt`), manifest + icônes placeholder, precache assets statiques, cache `NetworkFirst` pour `/api/`, composant `ReloadPrompt.vue`, meta tags PWA dans `index.html`, headers nginx `no-cache` pour `sw.js`
- **Revue frontend** : `apiFetch()` centralisé, toast erreurs, JWT expiry, `PromptModal`, types/formatters partagés, split `useBeaconEdit`, fix perf `SummaryCounters`, anti double-clic actions, lazy routes, CSS variables, cleanup dead code, Vitest (51 tests)
- **Refactoring architecture backend** : DI services, exceptions domaine, extraction `ResultsCalculator`, `LogService` partagé, typage `TemplateImportData`, fix mutation tracking, `HealthResponse`
- **Revue documentation** : specs techniques, modèle de données, decisions, CDC et vues alignés sur le code réel
- **Renommage `CheckpointEntry.timestamp` → `passage_time`** : backend, frontend et tests mis à jour

---

## 2026-07-31

- Onglet Horaires — drag & drop (`vuedraggable`) pour réordonner les participants
- Résultats publics masqués tant que tracker non rendu (backend + frontend)
- Vue Départ — masquage ligne tracker si aucun tracker assigné
- Lien public cliquable/copiable dans l'onglet Général
- Dernière PH : affichage en ligne unique (validation verte)
- Fix PH arrival edit : nouveau log `ph_arrival_edit` + endpoint dédié (auth + public)
- Fix `_enrich_courses()` : champ `code` inclus dans les balises enrichies
- Fix sync multi-encadrant : `watch(competitors)` appelle `syncInputs()` à chaque refresh WS
- Bouton Annuler (✗) par ligne dans `BeaconEditTable`
- Nom auteur dans l'historique (`LogMetadata.author_name` résolu par `TrackingService`)
- Refactoring PH dynamiques : `Beacon.gate` → `Beacon.is_ph`, labels PH calculés dynamiquement
- Fix perf `BeaconsTab` : `:key="beacon.id"`, suppression `reassignIds()`
- Vue publique Résultats + Édition balises (feature complète, 3 endpoints publics)
- Spec balises PH en 2 lignes (arrivée orange / départ vert)
- Docs : création `public_results.md`, `public_beacon_edit.md`

## 2026-07-30

- WebSocket temps réel : `ConnectionManager` + endpoint WS + reconnexion auto frontend (backoff, visibility-aware)
- Pinia store centralisé (`event-store.ts`) : cache intelligent, supprime les re-fetch entre vues
- Endpoint agrégé `GET /api/events/{id}/tracking` : élimine le problème N+1 (1 requête au lieu de 2+2N)
- Refactoring frontend : décomposition vues monolithiques (SuiviView -82%, DepartView -59%), nouveaux composables et sous-composants
- Alignement frontend sur la nouvelle structure des logs backend (`creation_date`, `passage_time`, `log_type`)
- Refactoring backend architecture clean : repos typés, services, thin controllers, élimination `list[dict]`
- Refactoring structure des logs : format imbriqué `{ log_type, metadata, data? }`, tri par `creation_date`
- Déduplication schémas : `CommentData`, `BaseRequest`, `NameBody` partagés
- `skills.md` : ajout règle §10 "Nommage explicite"
- Vue Suivi : accord genré "Arrivé/Arrivée", fix PH en cours, effacement code balise
- Fix crash 500 `/resultats` : timestamps `None` ignorés dans `_check_order()`
- Fix crash frontend `formatLogTimestamp()` : guard null
- Vue Suivi : touche Entrée déclenche enregistrement d'une ligne
- Endpoint `GET /registrations/{uid}/checkpoints` + `CheckpointService`
- Fix tri logs : tri par `received_at` au lieu de `timestamp`
- Vue Suivi : bouton ✓ par ligne (remplace "Enregistrer" global)
- Vue Suivi : format temps PH en HHhMM
- Vue Suivi : code et horaire de passage indépendants (fix bug modification horaire PH)
- Vue Départ : champ "Heure de départ réelle" dans le dépliant
- Refactoring API templates : endpoints GET/PUT dédiés par section (`/beacons`, `/courses`, `/time-gates`)
- Colonne ID dans tableau balises (auto-attribuée ≥ 31)
- Fix bug 422 création parcours template

## 2026-07-28

- Vue Suivi : balises éditables inline + bouton "Enregistrer", format HH:MM:SS, temps écoulé visible
- Vue Suivi : fix timestamp (utilise champ "Horaire de passage"), bouton ⏱ heure courante
- Schéma `checkpoint_edit` : champ `comment` optionnel
- Vue Suivi encadrant : horloge, liste triée, code couleur, dépliant PH/balises/abandon/tracker/historique/compteurs
- Endpoints actions d'épreuve : abandon, abandon-cancel, tracker-returned, tracker-returned-cancel, checkpoint-edit
- Vue Départ encadrant : horloge, code couleur, bouton DÉPART, dépliant édition inline
- Composant `EventHeader` : header sticky navigation Config/Départ/Suivi/Résultats
- Schémas logs : BaseLogEntry, DepartureLog, DepartureCancelLog, DnsLog, DnsCancelLog, BagWeightLog + union
- Endpoints logs : POST depart, depart-cancel, dns, dns-cancel, bag-weight + GET logs
- Endpoint `PATCH registrations/{uid}` : modification inline (course, horaire, tracker)
- Composable `useAuth` : extraction `getAuthHeaders()` (supprime 7 duplications)
- Typage strict schemas Pydantic : `Beacon`, `Course`, `CourseDetail`, `Gate`, `CourseTimeGates`
- Identifiant unique par balise (`id` ≥ 31), parcours par références d'id
- Enrichissement API : GET courses résout les ids en objets complets
- Auth : `role` dans JWT, dépendance `require_organizer`, guard frontend
- Onglet Participants : colonne « ID Routechoices », déduplication améliorée, import CSV
- Page admin_home : 2 onglets (Templates / Événements), `CreateModal`
- Endpoints CRUD templates + events (list, create, get, patch)
- Page config événement : 6 onglets + onglet Général (nom, date, template, heure, lien)
- Auth : `get_current_user`, guard frontend, redirection post-login
- Page config template : 3 onglets (Balises, Parcours, Temps PH)
- Endpoint `PATCH /api/templates/{id}` : mise à jour partielle
- Volume Docker `./backend/data:/app/data`
- Onglets événement : Balises (codes 2 lettres), Parcours, Barrières horaires
- Bouton "Initialiser depuis le template" + endpoint `POST import-template`
- Onglet Participants : tableau inline (nom, prénom, sexe, tel)
- Onglet Horaires : config mode départ, tableau ordonné, horaires calculés
- Endpoints `GET/POST/DELETE registrations`

## 2026-07-27

- Page login encadrant (`/login`) : formulaire pseudo + mot de passe
- Endpoint `POST /api/auth/login` : vérifie credentials, retourne JWT 12h
- User par défaut : `renaud` / `arvik` (mot de passe en clair dans `data/users.json`)
- Initialisation monorepo : `backend/` (FastAPI + uv) + `frontend/` (Vue 3 + Vite 6 + TS)
- `docker-compose.yml` : build depuis les Dockerfiles, ports 8000 + 3000
- Proxy nginx `/api` → backend
- Tests unitaires backend (health + auth)

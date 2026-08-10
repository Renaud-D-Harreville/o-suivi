# Changelog — O-Suivi

> Historique des modifications du projet.

---

## 2026-08-07

- **Normalisation horaires en HH:MM:SS** : suppression de la date dans tous les champs d'horaire de course (`departure_time`, `passage_time`, `ph_arrivals`). Backend : les `apply_to()` des 6 types de logs passent par `to_hms()` pour extraire HH:MM:SS de n'importe quel format (ISO ou déjà HH:MM:SS). Frontend : suppression de `hmsToIsoTimestamp()` et `formatIsoToHms()`, les composables envoient/reçoivent directement du HH:MM:SS. `useTimeGates` utilise le nouveau `secondsBetween()` frontend (arithmétique pure sur strings). `formatResultTime()` retourne directement le HH:MM. Tests mis à jour (166 backend, 100 frontend).
- **Fix : temps intermédiaires > 24h** : correction du calcul des splits et temps de section. `seconds_between()` n'utilise désormais que la composante horaire (HH:MM:SS) et ignore la date. Le problème venait de `hmsToIsoTimestamp()` (frontend) qui collait la date du jour de saisie sur un horaire, causant des écarts de plusieurs jours quand l'édition était faite après l'épreuve. Correction aussi de `_check_order()` dans `SectionValidator` pour comparer les temps sans la date. 21 tests unitaires ajoutés dans `test_time_utils.py`.

---

## 2026-08-05

- **Vue publique horaires** : nouvelle page `/events/{uuid}/schedule` permettant de consulter les horaires de départ prévus des stagiaires (sans authentification). Colonnes : horaire (gris), Prénom N. (anonymisé), téléphone. Backend : `ScheduleService`, `ScheduleEntry`/`ScheduleResponse` schemas, endpoint `GET /api/public/events/{id}/schedule`. Frontend : `PublicScheduleView.vue`, route, lien "📅 Horaires" ajouté dans la vue résultats publique. 3 tests backend ajoutés. Docs : `public_schedule.md`, CDC §5.5, `public_results.md` mis à jour.

---

## 2026-08-04

- **Fix : reconnexion automatique** : l'utilisateur déjà authentifié (token JWT valide en localStorage) est désormais redirigé automatiquement vers `/admin` quand il accède à `/` ou `/login`, au lieu de devoir re-saisir ses identifiants.
- **Lien retour vue encadrant sur les vues publiques** : composant `AdminBackLink.vue` affiché conditionnellement (token organizer valide) en haut à droite des 4 vues publiques. Pointe vers la vue admin correspondante (`/admin`, `/admin/events/:id/resultats`, `/admin/events/:id/suivi`). Docs mises à jour.
- **Vue publique résultats — adoucissement affichage** : suppression des ✅/❌ en liste (remplacés par "Arrivé"/"Arrivée" selon le sexe), suppression de la bannière PH (ligne 2). Tableau résumé par section : colonne "Statut" renommée "Codes" avec un nouveau champ backend `codes_valid` (vérifie uniquement les codes, indépendamment du temps). Backend : ajout `codes_valid` dans `SectionResult` + méthode dédiée `_compute_codes_validity` dans `SectionValidator`.
- **Anonymisation vues publiques** : les noms de famille sont tronqués à la première lettre + point (ex: "Marie D.") sur toutes les vues publiques (résultats, splits, édition balises). Fonction utilitaire `shortName()` dans `format.ts`.
- **Vue publique comparaison splits** : nouvelle page `/events/{uuid}/splits` permettant de comparer les temps intermédiaires de tous les concurrents, balise par balise. Un tableau par paire de balises consécutives (ordonnées par numéro/tag), classement par split croissant. Backend : `SplitCalculator` (domain), `SplitService` (orchestration), endpoint `GET /api/public/events/{id}/splits`. Frontend : `PublicSplitTimesView.vue`, types `splits.ts`, route + lien depuis la vue résultats publique. 5 tests backend ajoutés. Docs : `public_split_times.md`, CDC §5.5, `public_results.md` mis à jour.

---

## 2026-08-03

- **Fix : heure nulle dans le suivi** : correction du bug empêchant d'effacer un horaire de passage dans la vue Suivi encadrants. Extraction d'un utilitaire partagé `beacon-validation.ts` (validation format HH:MM:SS, détection de changement code/heure, conversion payload) mutualisé entre la vue admin et la vue publique d'édition des balises. 23 tests unitaires ajoutés.
- **Fix : validité balise après effacement** : correction du `BeaconAnalyzer` — un checkpoint dont le code et l'horaire ont été effacés (envoyés `null`) affichait ❌ (invalide) au lieu de `--` (pas de saisie). La méthode `_validity` traite désormais un checkpoint vide comme inexistant, et un code absent (avec temps présent) comme indéterminable (`valid=None`). 2 tests ajoutés.
- **Offline vue publique édition balises** : remplacement de `fetch()` natif par `apiFetch()` pour les mutations → les saisies de codes/horaires sont désormais enregistrées dans IndexedDB quand le réseau est indisponible et rejouées automatiquement. Mutualisation du composant `BeaconEditTable.vue` (prop `showValid`) entre la vue Suivi admin et la vue publique. Ajout du bouton ✗ (annuler) sur la vue publique.
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

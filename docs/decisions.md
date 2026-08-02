# Decisions Log — O-Suivi

> Architectural and design decisions agreed during the project.  
> Each entry records what was decided, why, and when.

---

## Format

```
### [DATE] — Title
**Decision**: What was decided
**Reason**: Why
**Impact**: What it affects
```

---

## Decisions

### 2026-07-23 — Code language is English

**Decision**: All code (variables, functions, classes, comments, commits) is in English. Documentation stays in French.  
**Reason**: Industry standard, easier tooling, potential for contributors. Docs are French because the domain vocabulary is specific to French mountain training.  
**Impact**: All source files, commit messages.

### 2026-07-22 — Departure is confirmed manually by organizer

**Decision**: A "Départ" button confirms each competitor's departure (not automatic based on scheduled time).  
**Reason**: Allows handling delays, last-minute changes, and logistics issues without being locked by an automatic mechanism.  
**Impact**: Vue Départ, chrono start for section 1.

### 2026-07-22 — Saisie différée deferred to backlog

**Decision**: The "deferred code entry" feature (for competitors without a phone) is out of v1 scope.  
**Reason**: Introduces too many edge cases (no timestamps, manual PH validation). The organizer can already edit codes via the Suivi view as a workaround.  
**Impact**: No additional UI needed for v1.

### 2026-07-21 — Routechoices integration deferred to v2

**Decision**: Only a simple URL link to Routechoices is kept in v1. Full GPS integration (tracking, proximity detection) is deferred.  
**Reason**: Simplifies v1 scope. The link provides value without technical complexity.  
**Impact**: No API integration needed. Just a URL field in event configuration.

### 2026-07-21 — creation_date-wins for conflict resolution

**Decision**: In case of simultaneous offline edits, the server processes actions in chronological order based on the device's local `creation_date`.  
**Reason**: More correct than "last write wins" for offline scenarios where sync is delayed. Combined with idempotent actions and full history.  
**Impact**: Sync mechanism, all offline actions carry `creation_date` (ISO 8601).

### 2026-07-23 — No "force" concept — unified writes with history

**Decision**: There is no dedicated "force PH" mechanism. All writes go through the same API. When an organizer writes/modifies data, a log entry is automatically created in the modification history.  
**Reason**: Simpler model. No need for force/cancel-force logic. History provides full traceability. Reverting = writing back the old value (also logged).  
**Impact**: Data model (no ForceLog table), API design, Vue Suivi.

### 2026-07-23 — JWT token duration: 12 hours

**Decision**: Organizer JWT access tokens last 12 hours. No refresh token mechanism.  
**Reason**: An event typically lasts ~10 hours. A single token covering the full day avoids re-login during the event.  
**Impact**: Auth configuration, security considerations.

### 2026-07-23 — WebSocket for real-time organizer updates

**Decision**: Use WebSocket for pushing real-time updates to the organizer's Suivi and Départ views. Visibility-aware auto-reconnection with exponential backoff. Manual "Se reconnecter" button as fallback. No automatic polling.  
**Reason**: More reactive, lower latency for tracking competitors. Simple enough given the low number of concurrent connections (5-10). Visibility-aware reconnection avoids battery drain when phone is in pocket.  
**Impact**: Backend WebSocket endpoint, frontend WebSocket client + reconnection composable, deployment (Cloud Run compatibility to validate).

### 2026-07-23 — Storage: JSON files (no relational DB)

**Decision**: Use flat JSON files for storage (no PostgreSQL, no ORM).  
**Reason**: Ultra-simple, no DB server to manage, easy to debug/inspect, sufficient for the low data volume (~50 competitors, ~1000 checkpoints per event). Concurrency handled via append-only logs with `creation_date`-based ordering.  
**Impact**: `04_modele_de_donnees.md` defines file structure. No SQLAlchemy/Alembic/asyncpg dependencies. Backend storage layer reads/writes JSON directly.

### 2026-07-26 — Routechoices ID as deduplication key

**Decision**: A `routechoices_id` field is added to the User model (optional for both organizers and competitors). It serves as the primary deduplication key when matching users across events.  
**Reason**: Name+first_name matching is fragile (typos, name changes). The Routechoices ID is a reliable external identifier already known in the ecosystem.  
**Deduplication priority**: routechoices_id first → name+first_name fallback.  
**Constraint**: Must be unique across all users. If a match by routechoices_id finds different name/first_name, the organizer is informed before update.  
**Impact**: `04_modele_de_donnees.md`, `views/events/participants.md` (CSV import + table), future CSV format.

### 2026-07-26 — API hybrid approach for event sourcing

**Decision**: Keep individual endpoints for each action type (checkpoint, ph-arrival, depart, abandon, etc.) + add a generic `POST .../log` endpoint for batch sync offline.  
**Reason**: Individual endpoints provide strong Pydantic validation and clear API documentation. The `/log` endpoint simplifies offline sync (one call to send all queued actions).  
**Key rules**:
- `author_id` is implicit (from JWT), never sent by client
- Client sends `creation_date` (local clock, ISO 8601). Server adds `received_at` for traceability
- Log file is append-only, **not sorted** on write. Sorting is done dynamically at read time by `creation_date`
- Batch sync: valid entries accepted, invalid returned as errors (partial success)
- Deduplication: `creation_date + type + sequence` — if already exists, entry is ignored (idempotent)  
**Impact**: `03_specifications_techniques.md` §4.3 rewritten. Backlog item removed.

### 2026-07-28 — Explicit template import via button (not automatic)

**Decision**: Template data (beacons, courses, time_gates) is imported into an event via an explicit "Initialiser depuis le template" button in the General tab. No automatic copy at event creation or template selection.  
**Reason**: Events are created with only a name (no template selected at creation time). An explicit button is safer — the user consciously decides to import/reset data. A confirmation popup explains the impact (existing beacons, courses, and time gates will be overwritten).  
**Impact**: `views/events/general.md` (new button + action), `views/events/beacons.md` §2 updated, `views/events/courses.md` §2 updated. New endpoint `POST /api/events/{id}/import-template`.

### 2026-07-28 — Shared navigation header across event views

**Decision**: All event views (Config, Départ, Suivi, Résultats) share a common sticky header with 4 navigation buttons. Each view is a separate route (`/admin/events/:id/config`, `/depart`, `/suivi`, `/resultats`).  
**Reason**: Keeps views separated (independent components, distinct responsibilities) while providing instant navigation between them. Simpler than tabs-within-tabs, more discoverable than hidden menus.  
**Impact**: `views/events/_overview.md` updated. Frontend: shared `EventHeader` component used by all 4 views. Router: 4 routes (config already exists, add 3 others).

### 2026-07-28 — Checkpoint edit comment is optional

**Decision**: The `comment` field in `checkpoint_edit` log entries is optional (can be null/omitted).  
**Reason**: When organizers correct beacon codes inline during live tracking, requiring a comment adds friction for a common action. The modification is already tracked in the history with `creation_date` and author.  
**Impact**: `04_modele_de_donnees.md` (comment?), `03_specifications_techniques.md`, backend schemas, `views/suivi.md` §4.3.

### 2026-07-28 — Inline beacon editing in Suivi view

**Decision**: Beacon codes and passage times are always editable inline (text inputs) in the Suivi view. Each row has a ✓ button to save individually. No batch save button.  
**Reason**: Saving per row avoids bugs when editing a row that isn't the last one with data. More predictable for the user.  
**Impact**: `views/suivi.md` §4.3 updated. Frontend: `SuiviView.vue` rewritten.

### 2026-07-30 — Log sorting by creation_date

**Decision**: `LogRepository` sorts logs by `metadata.creation_date` (client action time).  
**Reason**: `creation_date` represents when the action was performed by the user. This is the correct chronological ordering for state reconstruction. Note: `creation_date` is distinct from `passage_time` (which exists in `data` for `checkpoint_edit` and `ph_arrival_edit` entries and represents the corrected passage time, not the action time).  
**Impact**: `LogRepository.load()`, `GET /logs` endpoint.

### 2026-07-31 — Public access to results and beacon editing (no authentication)

**Decision**: A public page at `/events/{uuid}` allows anyone with the link to view all competitors' results and edit any competitor's beacons. No authentication required. Edits are traced with `author_id = "public"`.  
**Reason**: Simplifies sharing with competitors after/during the event. Allows collaborative beacon editing without requiring login. Acceptable security given the training context (not an official exam).  
**Impact**: New public API endpoints (no auth), new frontend views (`PublicResultsView`, `PublicBeaconEditView`), new `author_id = "public"` convention in logs.

### 2026-07-31 — Dynamic PH gates (variable number per course)

**Decision**: Replace the fixed 4 PH gates (PH1–PH4) with a dynamic model. Beacons are marked `is_ph: bool` (instead of `gate: "PH1"|"PH2"|...|null`). The PH number is computed dynamically based on the ordinal position of PH beacons within each course.  
**Reason**: Allow creation of circuits and events with varying numbers of sections, not just the standard 4-section probatoire blanc format. More flexibility for different types of training events.  
**Key changes**:
- Beacon field: `gate: string | null` → `is_ph: bool`
- Time gates per course: variable number of entries (one per PH beacon in the course)
- Gate labels ("PH1", "PH2", ...) are ordinal identifiers computed from position
- Min time bound is optional for ANY section (organizer's discretion), not just one specific section
- UI: PH dropdown replaced by checkbox  
**Impact**: Data model (templates + events JSON), all beacon/time_gates/courses views, backend schemas, domain logic (beacon_analyzer, section_validator, results_service), frontend types and composables. Existing data requires migration.

### 2026-08-02 — Dependency Injection via constructor parameters

**Decision**: Services receive their dependencies (repositories) as constructor parameters with default values. Pattern: `def __init__(self, events: EventRepository | None = None)` → creates default instance if None. This enables mocking in tests without `unittest.mock.patch`.  
**Reason**: Follows Dependency Inversion Principle. Makes dependencies explicit and testable. The default-value pattern avoids boilerplate at call sites while enabling injection in tests.  
**Impact**: All services (`results_service.py`, `tracking_service.py`, `checkpoint_service.py`, `registration_service.py`), all tests.

### 2026-08-02 — Domain exceptions instead of HTTPException in repositories

**Decision**: Repositories raise domain-specific exceptions (`EntityNotFound`) defined in `app/domain/exceptions.py`. FastAPI converts these to HTTP responses via a global exception handler in `main.py`. Repositories never import from `fastapi`.  
**Reason**: Separates infrastructure concerns (HTTP status codes) from data access. Repositories remain framework-agnostic, reusable, and testable without FastAPI context.  
**Impact**: `app/domain/exceptions.py` (new), `app/repositories/*`, `app/main.py` (exception handler).

### 2026-08-02 — Frontend global error handling pattern

**Decision**: Introduce a centralized `apiFetch()` wrapper that replaces all raw `fetch()` calls in the frontend. It handles: (1) automatic JWT auth header injection, (2) JWT expiration check before each call, (3) automatic redirect to `/login` on 401 responses, (4) network error surfacing via a global toast notification system. Additionally, replace all browser `prompt()` calls with a custom `PromptModal` component, and add CSS custom properties for design tokens.  
**Reason**: The app's #1 constraint is offline-first robustness. Without centralized error handling, network failures are silently swallowed — users get no feedback. Scattered 401 checks are inconsistent. `prompt()` is blocking, unstyled, and unreliable in PWA/mobile contexts. Hardcoded hex colors make design changes expensive.  
**Impact**: New files: `utils/api.ts`, `utils/clipboard.ts`, `composables/useToast.ts`, `composables/usePrompt.ts`, `components/ToastNotification.vue`, `components/PromptModal.vue`, `types/results.ts`, `styles/variables.css`. Refactored: all composables and views using raw `fetch()`, `SummaryCounters.vue` (performance), `useBeaconEdit.ts` (split), `router/index.ts` (lazy loading + JWT expiry), `env.d.ts` (cleanup).

### 2026-08-03 — Offline sync via individual endpoints (not batch /log)

**Decision**: Offline actions are replayed one-by-one via their normal REST endpoints (e.g. `POST .../depart`, `POST .../checkpoint-edit`) rather than a generic batch `POST .../log` endpoint.  
**Reason**: Each individual endpoint has strong Pydantic validation and clear semantics. No new backend code required — the frontend handles queuing and replay. Server-side deduplication (`creation_date + type + sequence`) already prevents duplicates.  
**Scope**: All event views (admin: Config, Départ, Suivi, Résultats) + public beacon editing views. Templates are excluded from offline support.  
**Impact**: Frontend only — new Dexie.js database with `pendingActions` queue + `eventCache` snapshot tables, sync engine composable, network status indicator. No backend changes.

### 2026-08-02 — PWA setup with vite-plugin-pwa (prompt update strategy)

**Decision**: Enable PWA support via `vite-plugin-pwa` using Workbox `generateSW` mode and `prompt` update strategy. Precache all static assets. Add `NetworkFirst` runtime caching for `/api/` requests (fallback to cache when offline). Add a `ReloadPrompt.vue` component to notify users of available updates. Add a web app manifest with icons for installability.  
**Reason**: The app must work in mountain environments without network. The `prompt` strategy (vs `autoUpdate`) is chosen because auto-updating the service worker mid-event could disrupt organizers during a live race — they should consciously decide to reload. `NetworkFirst` for API calls ensures the latest data when online, while still serving cached responses when offline. `generateSW` is simpler than `injectManifest` and sufficient for our caching needs.  
**Impact**: New deps: `vite-plugin-pwa`. New files: `frontend/public/pwa-192x192.png`, `frontend/public/pwa-512x512.png`, `frontend/src/components/ReloadPrompt.vue`. Modified: `vite.config.ts` (PWA plugin config), `index.html` (meta tags), `main.ts` (SW registration hint). Updated: `03_specifications_techniques.md` §3.3.


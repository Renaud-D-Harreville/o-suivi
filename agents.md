# Agents Guidelines — O-Suivi

> Instructions for AI agents working on this project.  
> **Last updated**: 2026-08-03

---

## 1. Project Context

**O-Suivi** is a web application for managing training events ("probatoires blancs") that prepare candidates for the official AMM (Accompagnateur en Moyenne Montagne) orientation test.

### What it does

- **Configure** training events (courses, checkpoints, participants)
- **Manage departures** of competitors sequentially
- **Track in real-time** each competitor's progress during the event
- **Display results** (provisional and final) to organizers and competitors

### Key constraints

| Constraint | Description |
|------------|-------------|
| **Offline-first** | Must work without internet (mountain environment). Bidirectional sync when network returns |
| **Multi-user** | Multiple organizers with equal rights, simultaneous access |
| **Robustness** | Manual fallback always possible. No data loss |
| **Simplicity** | Usable on the field, under stress, by non-technical users |

### Users

- **Encadrants (Organizers)**: Full access to all admin views (Configuration, Départ, Suivi, Résultats)
- **Stagiaires (Competitors)**: Can view results and edit beacons via shared public links (no authentication required)

### Documentation reference

All functional specifications are in `docs/`. Start with `docs/01_cahier_des_charges_fonctionnel.md` for the full picture, then refer to individual view specs in `docs/views/`.

---

## 2. Code Conventions

### Tech stack

| Composant | Technologie | Version cible |
|-----------|-------------|---------------|
| Frontend | Vue.js 3 + Vite (PWA) | Vue 3.x, Vite 6.x |
| State management | Pinia | 2.x |
| Offline storage | Dexie.js (IndexedDB) | 4.x |
| Backend | Python / FastAPI | Python 3.12+, FastAPI latest |
| Validation | Pydantic | 2.x |
| Auth | JWT (HS256, 12h) | python-jose or authlib |
| Storage | JSON files (no relational DB) | — |
| Hosting | GCP (Cloud Run / GCE) | — |
| Containers | Docker + Docker Compose | — |
| Real-time | WebSocket (organizers only) | — |

### General principles

- **Clean code**: readable, self-documenting, minimal comments (only for "why", not "what")
- **Class-based**: prefer classes over loose functions for domain logic
- **SOLID principles**: strictly follow Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Small files**: one class per file, one responsibility per file. If a file grows beyond ~150 lines, consider splitting
- **Package structure**: group related files into packages/modules. A package should represent a cohesive domain concept

### Naming

- Files: `snake_case` (Python) or `kebab-case` (JS/TS)
- Classes: `PascalCase`
- Functions/methods: `snake_case` (Python) or `camelCase` (JS/TS)
- Constants: `UPPER_SNAKE_CASE`
- Be explicit: prefer `CompetitorDepartureManager` over `Manager`

### Language

- **Code**: always in English (variables, functions, classes, comments, commit messages)
- **Documentation**: French (domain-specific vocabulary is French; translation to English may come later)
- No mixing: never use French in code, never use English in docs (unless for technical terms with no French equivalent)

### Architecture

- Separate **domain logic** from **infrastructure** (database, API, UI)
- Use dependency injection for testability
- Keep business rules in pure domain classes (no framework dependencies)
- Thin controllers/handlers: delegate to services immediately

### Error handling

- Explicit error types over generic exceptions
- Fail fast, fail loudly in development
- Graceful degradation in production (especially for offline scenarios)

---

## 3. Workflow

### ⚠️⚠️⚠️ MANDATORY PROCESS — FOR EVERY SINGLE NEW REQUEST ⚠️⚠️⚠️

> **THIS IS NOT OPTIONAL.** This workflow MUST be followed for EVERY new user request, without exception.  
> **Do NOT skip steps.** Do NOT jump to code. Do NOT assume agreement.  
> **Every request = full workflow from step 1 to step 8.** No shortcuts. No excuses.  
> If you ignore this process, you are failing at your job. Period.

```
1. UNDERSTAND      → Read docs, grasp context, ask questions if unclear
2. DOCUMENT PLAN   → Propose documentation updates (specs, views, decisions...)
3. AGREE (docs)    → Get user agreement on doc changes
4. CODE PLAN       → Propose code changes (files, structure, data models)
5. AGREE (code)    → Get user agreement on code changes
6. IMPLEMENT       → Write the code (only after agreement)
7. TEST            → Write tests for the new code
8. FINALIZE DOCS   → Update remaining documentation (changelogs, agents.md...)
```

### Rules

- **🚨 FOLLOW THE WORKFLOW ABOVE FOR EVERY NEW REQUEST. NO EXCEPTIONS. 🚨**
- **NEVER write code without explicit user consent.** Always present your plan first and wait for approval.
- **NEVER skip the UNDERSTAND step.** Always read the relevant docs first.
- **NEVER skip the DOCUMENT PLAN step.** Always propose doc changes before code changes.
- **NEVER skip the AGREE steps.** Always wait for explicit user approval before proceeding.
- **Spec conflict**: if you discover a contradiction or gap in the specs during implementation, **stop and ask the user** before writing anything. Do not guess or resolve it yourself.
- If the plan changes during implementation, stop and re-validate with the user.
- If unsure about a decision, ask. Do not guess.
- **Git**: the user manages git conventions and commits. Do not commit or suggest commit workflows.

### 🚨 ANTI-SKIP RULES 🚨

> **RE-READ `agents.md` FROM DISK (via `read_file` tool) AT EVERY SINGLE USER PROMPT. NO EXCEPTION.**
> **This is the FIRST thing you do before anything else. EVERY. SINGLE. TIME.**
> **"RE-READ" ALWAYS means reading from disk via `read_file` tool. NEVER from memory or context window.**

- **EVEN FOR "SMALL" CHANGES** (renaming a label, moving a field, changing a condition): FULL WORKFLOW. NO EXCEPTION.
- **A change to an existing feature IS a new request.** Restart from step 1.
- **NEVER call `insert_edit_into_file`, `replace_string_in_file`, or `create_file` before step 6.**
- **If you are about to write code, STOP. Check: did the user explicitly say "ok/go/yes" to BOTH step 3 AND step 5?** If not, you are violating the workflow.
- **At the start of every response**, mentally verify: "Which step am I at? Have I received explicit user agreement for all previous agree steps?" If the answer is no, DO NOT proceed to the next step.
- **Every "re-read" instruction in this file means: use the `read_file` tool to read the file from disk.** Never rely on memory or context window. This applies to `agents.md`, `skills.md`, and any other file referenced.


### Step 1 — Understand

- Read the relevant documentation to gather full context:
  - `docs/01_cahier_des_charges_fonctionnel.md` (primary source of truth)
  - `docs/views/*.md` (detailed view specs)
  - `docs/03_specifications_techniques.md` (architecture, API, stack)
  - `docs/04_modele_de_donnees.md` (data structures)
  - `docs/backlog.md` (deferred features, known gaps)
  - `docs/decisions.md` (past decisions and their rationale)
- Understand the user's request in the context of the existing specs
- Ask clarifying questions if anything is ambiguous or contradicts existing docs

### Step 2 — Document Plan

- Propose a plan to **update documentation first** (before any code):
  - Which docs need to change? (view specs, CDC, technical specs, decisions...)
  - What changes in each? (brief description)
- The goal: documentation should always reflect the desired state **before** code is written
- This ensures specs are the source of truth, not the code
- **Excluded from this step**: `CHANGELOGS.md` and `backlog.md` — these document what was done, not what will be done. They are updated at step 8 only.

### Step 3 — Agree (docs)

- Wait for the user to say "go", "ok", "yes", or equivalent
- If the user asks for changes, revise and re-present
- Once agreed, apply the documentation changes

### Step 4 — Code Plan

- **🔴 MANDATORY**: Re-read `skills.md` from disk (via `read_file` tool) before proposing. NOT from memory.
- List which code files will be created/modified
- Describe what changes in each (brief, no code)
- **Exception**: data models should be shown as code (we need to agree on structure)
- Identify potential impacts on existing code
- Keep it concise — just enough to understand the scope

### Step 5 — Agree (code)

- Wait for user agreement before writing any code
- If the user asks for changes to the plan, revise and re-present

### Step 6 — Implement

- **🔴 MANDATORY**: Re-read `skills.md` from disk (via `read_file` tool) before writing any code. NOT from memory.
- Follow code conventions (§2)
- Write clean, minimal, focused code
- One concern per commit/change

### Step 7 — Test

- Write unit tests for all new domain logic
- Write integration tests for critical paths
- Tests should be independent, fast, and deterministic

### Step 8 — Finalize Docs

Update any remaining documentation not covered in step 3:

| Document                                    | When to update                                                                |
|---------------------------------------------|-------------------------------------------------------------------------------|
| `docs/CHANGELOGS.md`                        | Every meaningful code change (keep a running log, one line per item, concise) |
| `docs/backlog.md`                           | Mark resolved items as ✅ done (with date)                                    |
| `agents.md` (this file)                     | Project structure changes, new conventions                                    |

---

## 4. Project Structure

```
o-suivi/
├── agents.md                          ← This file (agent instructions)
├── README.md                          ← Project overview
.├── docker-compose.yml                 ← Build & run (backend + frontend)
│
├── docs/
│   ├── 01_cahier_des_charges_fonctionnel.md   ← Functional spec (high-level)
│   ├── 03_specifications_techniques.md        ← Technical spec
│   ├── 04_modele_de_donnees.md                ← Data model
│   ├── CHANGELOGS.md                          ← Change history
│   ├── decisions.md                           ← Architectural/design decisions log
│   ├── backlog.md                             ← Deferred features & ideas
│   └── views/
│       ├── admin_home.md                      ← Admin home page (templates + events lists)
│       ├── depart.md                          ← Departure view spec
│       ├── suivi.md                           ← Tracking view spec
│       ├── resultats.md                       ← Results view spec
│       ├── public_results.md                  ← Public results view spec (no auth)
│       ├── public_beacon_edit.md              ← Public beacon edit view spec (no auth)
│       ├── templates/
│       │   ├── _overview.md                   ← Template navigation (3 tabs)
│       │   ├── beacons.md                     ← Beacon registry tab
│       │   ├── courses.md                     ← Courses tab
│       │   └── time_gates.md                  ← PH times tab
│       └── events/
│           ├── _overview.md                   ← Event navigation (6 tabs)
│           ├── general.md                     ← General info tab
│           ├── beacons.md                     ← Beacon registry + codes tab
│           ├── courses.md                     ← Courses tab (copied from template)
│           ├── participants.md                ← Participants tab
│           ├── schedule.md                    ← Departure schedule tab
│           └── time_gates.md                  ← Time gates override tab
│
├── backend/
│   ├── pyproject.toml                 ← Python deps (uv)
│   ├── uv.lock                        ← Lock file
│   ├── Dockerfile                     ← Production image
│   ├── data/
│   │   ├── users.json                 ← User storage (JSON)
│   │   ├── templates/                 ← One JSON file per template
│   │   └── events/                    ← One folder per event (event.json + logs/)
│   ├── app/
│   │   ├── main.py                    ← FastAPI app entrypoint
│   │   ├── config.py                  ← Settings (JWT, paths)
│   │   ├── dependencies.py            ← Auth dependency (get_current_user)
│   │   ├── routers/
│   │   │   ├── auth.py                ← POST /api/auth/login
│   │   │   ├── templates.py           ← GET/POST /api/templates, GET/PATCH /api/templates/{id}
│   │   │   ├── events.py             ← GET/POST /api/events, GET/PATCH /api/events/{id}, POST import-template
│   │   │   ├── registrations.py      ← GET/POST/DELETE/PUT/PATCH /api/events/{id}/registrations, GET checkpoints
│   │   │   ├── logs.py               ← POST actions d'épreuve (départ, DNS, abandon, tracker, checkpoints, PH…) + GET logs
│   │   │   ├── public.py             ← Endpoints publics sans auth (résultats, checkpoints, éditions balises/PH)
│   │   │   └── ws.py                 ← WebSocket endpoint /api/events/{id}/ws (real-time refresh signal)
│   │   ├── websocket/
│   │   │   └── connection_manager.py ← ConnectionManager (manages WS connections per event, broadcasts refresh)
│   │   ├── services/
│   │   │   ├── results_service.py     ← Calcul des résultats (orchestration)
│   │   │   ├── tracking_service.py    ← Données de suivi agrégées (endpoint /tracking)
│   │   │   ├── checkpoint_service.py  ← Récupération des checkpoints d'un concurrent
│   │   │   ├── log_service.py         ← Création/append de logs (partagé admin + public)
│   │   │   └── registration_service.py ← Logique inscriptions (CRUD, déduplication, matching)
│   │   ├── domain/
│   │   │   ├── exceptions.py          ← Exceptions domaine (EntityNotFound)
│   │   │   ├── competitor_state.py    ← CompetitorState + CheckpointEntry (reconstruction depuis logs)
│   │   │   ├── beacon_analyzer.py     ← Analyse des passages balises
│   │   │   ├── section_validator.py   ← Validation des sections PH
│   │   │   ├── results_calculator.py  ← Logique métier résultats (validité, finish, tri)
│   │   │   └── time_utils.py          ← Utilitaires temps
│   │   ├── repositories/
│   │   │   ├── event_repository.py    ← CRUD événements (objets typés)
│   │   │   ├── template_repository.py ← CRUD templates (objets typés)
│   │   │   ├── log_repository.py      ← Chargement + append logs (tri par creation_date)
│   │   │   └── user_repository.py     ← CRUD utilisateurs (cache + persistance)
│   │   └── schemas/
│   │       ├── auth.py                ← TokenPayload / LoginRequest / LoginResponse
│   │       ├── common.py             ← HealthResponse
│   │       ├── templates.py           ← Beacon(is_ph) / Course / CourseDetail / Gate / CourseTimeGates / NameBody (=TemplateCreate=TemplateUpdate) / TemplateSummary / TemplateImportData
│   │       ├── events.py             ← StartMode / EventRegistration / EventBeacon(Beacon) / EventCreate(=NameBody) / EventSummary / EventDetail / EventUpdate
│   │       ├── registrations.py      ← RegistrationCreate / RegistrationDetail / RegistrationUpdate
│   │       ├── users.py              ← User
│   │       ├── results.py            ← BeaconResult / SectionResult / CompetitorResult / ResultsResponse
│   │       ├── tracking.py           ← CompetitorTracking / TrackingResponse
│   │       └── logs.py               ← Event sourcing : métadonnées (LogMetadata), entrées de log polymorphiques (discriminated union LogEntry), et schémas de requête client
│   └── tests/
│       ├── test_health.py
│       ├── test_auth.py
│       ├── test_templates.py
│       ├── test_events.py
│       ├── test_registrations.py
│       ├── test_logs.py
│       ├── test_tracking.py
│       └── test_public.py
│
└── frontend/
    ├── package.json                   ← Node deps
    ├── vite.config.ts                 ← Vite config (proxy /api, PWA plugin)
    ├── tsconfig.json                  ← TypeScript config
    ├── Dockerfile                     ← Production image (nginx)
    ├── nginx.conf                     ← Nginx config (SPA + proxy /api + SW no-cache)
    ├── index.html                     ← HTML shell (PWA meta tags)
    ├── vitest.config.ts               ← Vitest test configuration
    ├── public/
    │   ├── pwa-192x192.png            ← PWA icon 192×192 (placeholder)
    │   └── pwa-512x512.png            ← PWA icon 512×512 (placeholder)
    └── src/
        ├── main.ts                    ← Vue bootstrap + router
        ├── App.vue                    ← Root component (<router-view>)
        ├── env.d.ts                   ← Type declarations
        ├── stores/
        │   └── event-store.ts         ← Pinia store (current event: name, courses, timeGates, competitors) + IndexedDB cache fallback
        ├── types/
        │   ├── event.ts               ← Beacon, Course, TimeGateEntry, TimeGates
        │   ├── competitor.ts          ← CompetitorBeacon, CheckpointState, TrackingCompetitor
        │   ├── log.ts                 ← LogMetadata, LogEntry, BeaconInput
        │   └── results.ts            ← BeaconResult, SectionResult, CompetitorResult, PublicCompetitorResult, ResultsData, TemplateSummary, EventSummary
        ├── offline/
        │   ├── db.ts                  ← Dexie database (pendingActions, eventCache, eventListCache tables)
        │   ├── pending-action.ts      ← PendingAction interface
        │   ├── event-cache-service.ts ← Read/write event snapshots in IndexedDB
        │   ├── sync-engine.ts         ← Offline queue replay, sync triggers, network state refs
        │   └── __tests__/
        │       ├── db.test.ts
        │       ├── event-cache-service.test.ts
        │       └── sync-engine.test.ts
        ├── utils/
        │   ├── api.ts                 ← apiFetch() — centralized fetch wrapper (auth, 401, toast, offline queue for mutations)
        │   ├── clipboard.ts           ← copyToClipboard, copyPhone
        │   ├── date.ts                ← Date formatting helpers (toLocalISO, formatTime, formatMinutes, etc.)
        │   ├── format.ts             ← Results formatting helpers (formatDuration, formatResultTime, formatDelay, globalIcon, sectionIcon, beaconIcon)
        │   ├── competitor-state.ts    ← State reconstruction (buildCompetitorBeacons, computeCurrentPh, reconstructTrackingState)
        │   └── __tests__/
        │       ├── date.test.ts       ← Unit tests for date utilities
        │       ├── format.test.ts     ← Unit tests for format utilities
        │       └── competitor-state.test.ts ← Unit tests for competitor state logic
        ├── styles/
        │   └── variables.css          ← CSS custom properties (design tokens)
        ├── composables/
        │   ├── useAuth.ts             ← Auth composable (getAuthHeaders)
        │   ├── useClock.ts            ← Real-time clock (currentTime ref, auto tick/cleanup)
        │   ├── useTimeGates.ts        ← PH time gate logic (elapsed, status, color, row class)
        │   ├── useBeaconEdit.ts       ← Inline beacon editing (inputs sync, hasChanged)
        │   ├── useBeaconSave.ts       ← Beacon save logic (API calls for checkpoint/PH edits)
        │   ├── useCompetitorActions.ts ← Suivi actions (abandon, tracker returned) + pending guard
        │   ├── useInlineEdit.ts       ← Generic inline field editing (edit/cancel/save state)
        │   ├── useDepartureActions.ts ← Departure actions (depart, DNS, registration edits) + pending guard
        │   ├── useToast.ts            ← Global toast notifications (error/success/info)
        │   ├── usePrompt.ts           ← Custom prompt modal (replaces browser prompt())
        │   ├── useOfflineStatus.ts    ← Offline status composable (online, syncing, pendingCount, syncNow)
        │   └── use-websocket.ts       ← WebSocket composable (connect, reconnect with backoff, visibility-aware)
        ├── router/
        │   └── index.ts               ← Routes (/login, /admin, /admin/events/:id/config, /depart, /suivi) + auth guard
        ├── components/
        │   ├── CreateModal.vue        ← Reusable creation popup (name field)
        │   ├── EventHeader.vue        ← Shared sticky header (back + event name + Config/Départ/Suivi/Résultats nav)
        │   ├── ToastNotification.vue  ← Global toast notifications (auto-dismiss, error/success/info)
        │   ├── PromptModal.vue        ← Custom prompt modal (replaces browser prompt())
        │   ├── ReloadPrompt.vue       ← PWA update prompt (new SW version available → reload)
        │   ├── OfflineIndicator.vue   ← Offline status bar (🟢/🔴/🔄 + pending count + sync button)
        │   ├── suivi/
        │   │   ├── PhTable.vue        ← Time gates table for one competitor
        │   │   ├── BeaconEditTable.vue ← Inline beacon code/time editing table
        │   │   ├── CompetitorActions.vue ← Abandon + tracker buttons
        │   │   ├── CompetitorHistory.vue ← Modification history list
│   │   └── SummaryCounters.vue ← Departed/in-course/arrived/DNS/abandon counters
│       └── views/
            ├── LoginView.vue          ← Login page (organizers)
            ├── public/
            │   ├── PublicResultsView.vue   ← Public results (no auth, masking non-arrived)
            │   └── PublicBeaconEditView.vue ← Public beacon edit (no auth, PH 2-line, no valid column)
            └── admin/
                ├── AdminHomeView.vue  ← Admin home (tabs: Templates + Events)
                ├── DepartView.vue     ← Departure management (clock, competitor list, inline editing, actions)
                ├── SuiviView.vue      ← Tracking orchestrator (delegates to suivi/ sub-components)
                ├── ResultatsView.vue  ← Results display view
                ├── EventConfigView.vue ← Event config (6 tabs shell + header)
                ├── TemplateConfigView.vue ← Template config (3 tabs shell + header)
                ├── event-tabs/
                │   ├── GeneralTab.vue     ← General info form + "Initialiser depuis le template" button
                │   ├── BeaconsTab.vue     ← Beacon registry + 2-letter codes (editable table)
                │   ├── CoursesTab.vue     ← Course grid (beacons × courses)
                │   ├── ParticipantsTab.vue ← Participant list (inline add/delete)
                │   ├── ScheduleTab.vue    ← Start mode config + ordered schedule (↑↓, courses, times)
                │   └── TimeGatesTab.vue   ← Reference + adjusted times + percentages
                └── template-tabs/
                    ├── BeaconsTab.vue      ← Beacon registry (editable table)
                    ├── CoursesTab.vue      ← Course grid (beacons × courses)
                    └── TimeGatesTab.vue   ← PH time limits per course (min/max H/F)
```

> ⚠️ This structure will evolve as development begins. Update this section whenever files/folders are added.

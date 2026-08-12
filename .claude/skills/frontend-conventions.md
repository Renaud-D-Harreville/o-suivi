---
name: frontend-conventions
description: Vue 3/TypeScript coding conventions for the O-Suivi frontend. Invoke before writing or reviewing frontend code.
---

# Frontend Conventions (Vue 3 / TypeScript)

## Component patterns

- **Composition API with `<script setup>`** — all components use `<script setup lang="ts">`.
- **Views vs Components**: views (`views/`) are full-page screens routed by vue-router. Components (`components/`) are shared, reusable UI elements.
- **Admin vs Public views**: admin views require authentication (`views/admin/`). Public views are accessible without auth (`views/public/`).
- **Tab-based configuration**: event and template config views use sub-tab components (`event-tabs/`, `template-tabs/`).

## State management

- **Pinia** for global state (`stores/event-store.ts`) — current event data, courses, timeGates, competitors.
- **IndexedDB cache fallback** via Dexie.js for offline support.
- **Composables** (`composables/`) for reusable stateful logic (auth, clock, toast, inline editing, actions, WebSocket).

## Offline support

- **Dexie.js** (IndexedDB) for offline storage (`offline/`).
- Pending actions queue for mutations while offline.
- Event cache for read access without network.
- Sync engine replays queued actions when network returns.

## Routing

- **vue-router** with auth guard in `router/index.ts`.
- Routes: `/login`, `/admin`, `/admin/events/:id/config`, `/depart`, `/suivi`, plus public routes.

## Type safety

- Strict TypeScript — no `any`, no implicit `any`.
- Define proper interfaces and types in `types/` for all data structures.
- Props and emits must be fully typed.
- Use `defineProps<T>()` and `defineEmits<T>()` with type-only syntax.

## Naming

- Comprehensive, explicit names — no abbreviations.
- Components: PascalCase filenames (e.g., `DepartView.vue`, `PhTable.vue`).
- Composables: camelCase with `use` prefix (e.g., `useAuth.ts`, `useToast.ts`).
- Utilities: kebab-case filenames (e.g., `beacon-validation.ts`, `competitor-state.ts`).

## Code style

- Reuse existing patterns before introducing new abstractions.
- Write minimal, focused code — no features beyond what the task requires.
- No dead code, no commented-out code.
- Keep templates clean — extract complex logic into composables or computed properties.
- CSS custom properties (design tokens) in `styles/variables.css`.

## Testing

- Framework: **Vitest** with **happy-dom** and `@vue/test-utils`
- Run: `cd frontend && npm test`
- Build check: `cd frontend && npm run build`
- Tests live in `__tests__/` directories alongside the code they test (e.g., `utils/__tests__/`, `offline/__tests__/`).
- Follow existing test patterns.
- Mock external dependencies (APIs, browser APIs) but not the code under test.
- Use `fake-indexeddb` for IndexedDB-dependent tests.

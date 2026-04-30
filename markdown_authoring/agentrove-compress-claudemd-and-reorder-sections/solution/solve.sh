#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agentrove

# Idempotency guard
if grep -qF "- When query keys include optional dimensions (e.g., `cwd`), add a separate pref" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -8,96 +8,92 @@
 - Redis is for pub/sub and caching only — not a task broker or coordination layer
 - Background work runs as asyncio tasks in the API process
 - Treat per-user request handling as effectively sequential — don't flag bugs that only appear under overlapping concurrent requests (retries, double-submit, multi-tab) unless the task explicitly asks for concurrency hardening
-- ACP `field_meta` (`_meta`) is extensibility metadata agents aren't required to read — don't use it for user-facing data (alt instructions, form answers); if ACP has no first-class field for a concept, it can't be reliably done through metadata
+- ACP `field_meta` (`_meta`) is extensibility metadata agents aren't required to read — don't use it for user-facing data; if ACP has no first-class field for a concept, it can't be reliably done through metadata
 
-## SQLAlchemy Model Conventions
-
-- Always pair `default=` with `server_default=` — `default` only applies in Python/ORM
-- Always specify `nullable=True|False` explicitly
-- Always set max length on String fields (e.g., `String(64)`)
-- Use `DateTime(timezone=True)` for all datetime fields
-- Don't add `index=True` on an FK if a composite index already starts with that column
-
-## Migration Workflow
+## Minimalism
 
-- Generate migrations via Alembic autogenerate (don't write them by hand); manual edits to generated migrations are fine when needed for correctness
-- Run Alembic commands inside the Docker backend container (not on host)
-
-## Code Style
-
-### Minimalism
-- Choose the smallest fix — don't refactor, restructure, or add abstractions as part of a bug fix; prefer a one-line guard over reworked control flow
+- Choose the smallest fix — don't refactor or add abstractions as part of a bug fix; prefer a one-line guard over reworked control flow
 - Don't optimize for "no regressions" or long-term resilience unless asked — favor simple, direct changes over defensive scaffolding
-- Don't build elaborate rollback/state-restoration for failure paths — log + best-effort recovery (e.g., re-queue) is sufficient; don't save/restore every field, delete orphaned rows, or revert intermediate changes
-- Don't add resource cleanup (`try/finally` with `.cleanup()`, `.close()`) for short-lived provider/client objects — GC handles lazy clients (e.g., `aiodocker.Docker`); only add cleanup for long-lived or pooled objects
-- Don't add pre-flight compatibility checks when a natural fallback exists — let it fall through to the existing path instead of branching to re-route
+- Don't build elaborate rollback/state-restoration for failure paths — log + best-effort recovery (e.g., re-queue) is sufficient
+- Don't add resource cleanup (`try/finally` with `.cleanup()`/`.close()`) for short-lived provider/client objects — GC handles lazy clients (e.g., `aiodocker.Docker`); only add cleanup for long-lived or pooled objects
+- Don't add pre-flight compatibility checks when a natural fallback exists — let it fall through instead of branching to re-route
 - Validate at the boundary only — if an API endpoint checks a value, downstream functions receiving it shouldn't re-validate
 - Prefer the simplest collection op (e.g., `list.insert(0, item)` over a sorted-insertion loop when order doesn't matter)
 - Don't add backward-compat paths, fallback paths, or legacy shims unless asked
 - Don't create type aliases with no semantic value (e.g., `StreamKind = str`)
 - Don't handle hypothetical input shapes — code for the format you've observed (logs, tests, types), not branches for unseen structures
-- Avoid no-op pass-through wrappers; wrappers must add concrete value (validation, transformation, error handling, compatibility boundary, stable public API); prefer direct imports/calls otherwise
+- Avoid no-op pass-through wrappers; wrappers must add concrete value (validation, transformation, error handling, compatibility boundary, stable public API)
 - Don't extract a utility file for a single constant/expression duplicated across only 2 call sites — inline until 3+ sites or an existing file fits naturally
-- Don't create standalone functions that only wrap a single dict lookup with a default — inline `DICT[key].field` or `DICT.get(key)`; for tuples, use a `NamedTuple` instead of accessor functions
+- Don't create standalone functions that only wrap a single dict lookup with a default — inline `DICT[key].field` or `DICT.get(key)`; for tuples, use a `NamedTuple`
 - Don't create inline dict literals for identity mappings — use a module-level `frozenset` membership check
 
+## Completion Quality Gate
+
+- No dead code left behind — remove unused functions, exports, imports, constants, types, files, and stale wrappers in the same task
+- Every task includes a final dead-code sweep across touched areas and new files
+- Before finishing, verify:
+  - New symbols are referenced (or intentionally public and documented)
+  - Replaced symbols are removed and references updated
+- If something is intentionally left unused for compatibility, state that explicitly in the final summary
+
+## Verification
+
+- Don't run tests, lints, type checks, or similar verification commands unless explicitly asked
+
+## Code Style
+
+### Comments
+- Never use docstrings (`"""..."""`) — always use inline `#` comments
+- Always comment non-obvious logic, implicit conventions, design decisions — comment the *why*, never the *what*
+- Keep comments short — 1–2 lines max. If it needs more, simplify the code or move detail to the PR description
+- Don't delete existing comments without asking — they may capture context not obvious from the code
+- Prefer clear names over comments when code is self-explanatory
+- No decorative section comments (e.g., `# ── Section ──────`)
+- Place comments inside methods/classes, not above them — method comments are the first line in the body, explaining *why* and context (not restating the name)
+- Good: `# Read from the API host, not the sandbox — sandbox containers don't have the user's global git config`
+- Bad (restates name): `# Yield persisted events after a given seq`
+
 ### Exceptions
-- Keep `try/except` narrow — wrap only the code needing the specific recovery; code that can safely propagate should stay outside the `try`
+- Keep `try/except` narrow — wrap only the code needing the specific recovery; safely-propagating code stays outside the `try`
 - Narrow `except` clauses to specific types — never `except Exception` when failure modes are known
-- Don't translate exceptions across boundaries just to change the type — let meaningful upstream errors propagate; catch-and-wrap only when the caller needs a different status/shape
+- Don't translate exceptions across boundaries just to change the type — catch-and-wrap only when the caller needs a different status/shape
 - When catching a `ServiceException` subclass at the API boundary, use `exc.status_code` — don't hardcode a status that shadows the exception's classification
 - When a function receives an optional targeting parameter (e.g., `cwd`, `workspace_id`) and the value is invalid, raise — don't silently fall back to a default target
 
 ### Input & Security
 - Don't use Python `str.format()` or f-strings to interpolate untrusted content that may contain `{`/`}` (diffs, code, JSON) — use concatenation or `string.Template`
 - Add `Field(max_length=...)` to all `str` fields on Pydantic request models; add `min_length=1` when empty is invalid
 
-### FastAPI
-- Don't instantiate services in route handlers — add a factory in `deps.py` and inject via `Depends()`; route files shouldn't import `SessionLocal`
-- Don't define helper functions in endpoint files — endpoint files contain only route handlers. Inline no-op exception-translation wrappers at the call site; move reusable access/service helpers to `deps.py`; move pure utilities to `utils/`
-- When multiple endpoints share parameter validation (e.g., token presence), extract a FastAPI dependency that raises on failure and returns the validated value — don't duplicate inline
-
 ### Imports, Typing, Structure
 - No inline imports unless needed to break a circular import
-- Strong typing only — no `# type: ignore`, `# pyright: ignore`, `# noqa` to silence typing/import issues; fix types directly (document in PR if truly unavoidable)
-- Don't define nested/inline functions — use module-level functions or class methods (static/instance); a helper only used by a class must be a method on it
+- Strong typing only — no `# type: ignore`, `# pyright: ignore`, `# noqa` to silence typing/import issues; fix types directly
+- Don't define nested/inline functions — use module-level functions or class methods; a helper only used by a class must be a method on it
 - Module-level constants go at the top of the file, right after imports/logger/settings — never between classes or functions
 - Don't call private methods (`_method`) across files; make them public (and rename) if cross-file use is needed
-- Don't use `TypedDict` with `total=False` when all keys are always present — use `total=True`
-- When a Pydantic response model field has a default, the corresponding frontend TypeScript type must mark it required — the API always sends it
+- Don't use `TypedDict` with `total=False` when all keys are always present
+- When a Pydantic response model field has a default, the corresponding frontend TypeScript type must mark it required
 - Don't introduce a new frontend type when an existing one has the same shape — reuse directly across modules
-- When defining an abstract method signature during a refactor, verify every parameter gets a meaningful value from all call sites — don't carry forward parameters that are always hardcoded to `None`
+- When defining an abstract method signature during a refactor, verify every parameter gets a meaningful value from all call sites
 
-### Comments
-- Never use docstrings (`"""..."""`) — always use inline `#` comments
-- Always comment non-obvious logic, implicit conventions, design decisions — mandatory for new/modified code; comment the *why*, never the *what*
-- Keep comments short and punchy — 1–2 lines max. Compress to the essential *why*; no multi-paragraph explanations, no restating the surrounding code, no narrating the history of the change
-- If a comment needs more than two lines, the code itself probably needs simplifying or the detail belongs in the PR description, not the file
-- Don't delete existing comments without asking — they may capture context not obvious from the code
-- Prefer clear names over comments when the code is self-explanatory
-- No decorative section comments (e.g., `# ── Section ──────`) — code structure should be self-evident
-- Place comments inside methods/classes, not above them — a method comment is the first line inside the body
-- Method comments explain *why* and *context* (who uses it, non-obvious behavior), not just restate the name
-- Good: `# Read from the API host, not the sandbox — sandbox containers don't have the user's global git config`
-- Good method comment: `# Catch-up for SSE reconnection: pages persisted events after last-seen seq before switching to live pub/sub.`
-- Bad method comment (restates name): `# Yield persisted events after a given seq`
-- Bad (too long): a 4-line comment explaining every branch and edge case — collapse to one line naming the *why*
-- Example needing no comment: `user_dir.mkdir(parents=True, exist_ok=True)`
+### FastAPI
+- Don't instantiate services in route handlers — add a factory in `deps.py` and inject via `Depends()`; route files shouldn't import `SessionLocal`
+- Endpoint files contain only route handlers. Inline no-op exception-translation wrappers at the call site; move reusable access/service helpers to `deps.py`; move pure utilities to `utils/`
+- When multiple endpoints share parameter validation (e.g., token presence), extract a FastAPI dependency that raises on failure and returns the validated value
 
 ### Cross-cutting gotchas
 - When two methods in the same class share a lifecycle (one always calls the other), don't duplicate work in the caller that the callee already performs
-- When refactoring code with `try/catch/finally`, preserve cleanup in `finally` — don't move cleanup after an `await` without wrapping in `try/finally`
-- When extracting a shared utility from multiple callers with slightly different semantics, verify equivalence for every caller — especially edge-case inputs (`null`, `undefined`, `0`, `""`)
-- When spreading a caller-provided options object into a builder, use `Omit<>` to exclude keys the factory controls — prevents silent shadowing at the type level (not runtime `_ignored` destructuring)
+- When refactoring `try/catch/finally`, preserve cleanup in `finally` — don't move cleanup after an `await` without wrapping in `try/finally`
+- When extracting a shared utility from multiple callers with slightly different semantics, verify equivalence for every edge-case input (`null`, `undefined`, `0`, `""`)
+- When spreading a caller-provided options object into a builder, use `Omit<>` to exclude keys the factory controls — prevents silent shadowing at the type level
 - When a caller passes a value to a function that already stores/registers it, don't call a second function to store/register it again
-- When adding new operations in a domain that already accepts a context/targeting parameter (e.g., `cwd` for worktree paths), propagate it through the full chain — backend endpoint, frontend service, React Query hook, UI component
+- When adding new operations in a domain that already accepts a context/targeting parameter (e.g., `cwd`), propagate it through the full chain — backend endpoint, frontend service, React Query hook, UI component
 - Don't extract a shared React hook when callers must add `useCallback`/`useMemo` wrappers that the inline version didn't need
 - When closing/tearing down multiple independent resources in a loop, use `asyncio.gather(*[...], return_exceptions=True)` — don't serialize independent I/O
 - Prefer env-var/config solutions over runtime introspection (e.g., `HOST_STORAGE_PATH` to map container→host paths, not inspecting Docker mounts at runtime)
-- In JSX conditionals with numeric values, use explicit checks (`value != null && value > 0`) — not truthy checks, since `0` renders as text in React
-- In shell command chains, use `&&` to gate dependent steps and wrap independent cleanup in `{ ...; }` when exit status must reflect earlier failures — a bare `;` lets later commands mask upstream failures
-- When a shell/CLI command interpolates a path, confirm the cwd matches the path's basis — mixing repo-root-relative pathspecs with a nested cwd (or vice versa) silently scopes operations wrong
-- When adding a bulk variant of a per-item operation, mirror every edge case the per-item version handles (initial state, missing ref, newly-added vs tracked entries) — don't ship only the happy path
+- In JSX conditionals with numeric values, use explicit checks (`value != null && value > 0`) — `0` renders as text in React
+- In shell command chains, use `&&` to gate dependent steps and wrap independent cleanup in `{ ...; }` when exit status must reflect earlier failures
+- When a shell/CLI command interpolates a path, confirm the cwd matches the path's basis — mixing repo-root-relative pathspecs with a nested cwd silently scopes operations wrong
+- When adding a bulk variant of a per-item operation, mirror every edge case (initial state, missing ref, newly-added vs tracked entries)
 
 ## Naming Conventions
 
@@ -110,18 +106,31 @@
 
 ## Module Organization
 
-- Keep logic in the module where it belongs — factory methods go on the class they construct (e.g., `Chat.from_dict`, `SandboxService.create_for_user`)
-- Group related free functions into a class with static methods (e.g., `StreamEnvelope.build()` + `StreamEnvelope.sanitize_payload()` instead of two loose module functions)
-- Prefer one data structure over two when one serves both purposes — derive properties from existing data (e.g., `path.is_relative_to(base_dir)`) instead of tracking a parallel set; don't maintain overlapping containers for the same concept
+- Keep logic where it belongs — factory methods go on the class they construct (e.g., `Chat.from_dict`, `SandboxService.create_for_user`)
+- Group related free functions into a class with static methods (e.g., `StreamEnvelope.build()` + `StreamEnvelope.sanitize_payload()`)
+- Prefer one data structure over two when one serves both purposes — derive properties (e.g., `path.is_relative_to(base_dir)`) instead of tracking a parallel set
 - **`utils/`** — stateless pure functions only (parsing, formatting, validation). No I/O, DB, services, or HTTP concerns. Raise `ValueError`; let callers translate.
 - **`services/`** — stateful I/O-bound business logic (DB, API calls, sandbox commands). Instantiated with dependencies, injected via `Depends()`. Raise domain exceptions (`SandboxException`, `ChatException`, ...).
 - **`core/deps.py`** — FastAPI DI wiring; instantiate services, validate access, translate domain exceptions to `HTTPException` at the boundary.
 - **`core/security.py`** — auth/authz (token validation, password hashing, encryption, WebSocket auth handshake).
-- If a function does I/O or depends on a service, it doesn't belong in `utils/` — move it to a service class or `core/`
-- When a service accumulates responsibilities from two distinct domains, extract the secondary into its own service (e.g., `GitService` split out from `SandboxService`, with `GitService` depending on `SandboxService` for command execution)
-- Endpoint files contain only route handlers — all business logic (command building, output parsing, branching) belongs in services; endpoints handle HTTP concerns (validation, response formatting, exception translation)
+- If a function does I/O or depends on a service, it doesn't belong in `utils/`
+- When a service accumulates responsibilities from two distinct domains, extract the secondary into its own service (e.g., `GitService` split from `SandboxService`)
+- Endpoint files contain only route handlers — all business logic belongs in services
 - Place class definitions (including `NamedTuple`/`TypedDict`) at the top of the file after imports — never between constants
 
+## SQLAlchemy Model Conventions
+
+- Always pair `default=` with `server_default=` — `default` only applies in Python/ORM
+- Always specify `nullable=True|False` explicitly
+- Always set max length on String fields (e.g., `String(64)`)
+- Use `DateTime(timezone=True)` for all datetime fields
+- Don't add `index=True` on an FK if a composite index already starts with that column
+
+## Migration Workflow
+
+- Generate migrations via Alembic autogenerate (don't write them by hand); manual edits to generated migrations are fine when needed for correctness
+- Run Alembic commands inside the Docker backend container (not on host)
+
 ## Frontend Component Architecture
 
 ### React Version
@@ -133,7 +142,7 @@
 ### Composition Patterns
 - Avoid boolean prop proliferation (`isX`, `showX`, `hideX`) — use composition instead
 - When a component exceeds ~10 props or has 3+ boolean flags, refactor to a context provider + compound components
-- Use the `state / actions` context interface pattern: `{ state: StateType; actions: ActionsType }` so UI consumes a generic interface
+- Use the `state / actions` context interface pattern: `{ state: StateType; actions: ActionsType }`
 - Context definitions go in `*Definition.ts`, providers in `*Context.tsx` / `*Provider.tsx`, consumer hooks in `hooks/use*.ts`
 - Consumer hooks use React 19 `use()` and throw if context is null (see `useChatSessionContext.ts`)
 - Provider values must be `useMemo`'d to prevent unnecessary re-renders
@@ -147,7 +156,7 @@
 ### No Fallback Patterns in Context Interfaces
 - Context interface fields must not be optional (`?`) when the provider always supplies them
 - Don't add nullability guards (`value && doSomething()`) on context values guaranteed by the provider
-- Don't add `?? null` / `?? false` / `?? []` coercions in the provider unless the upstream genuinely returns `undefined` and the context type requires a concrete value
+- Don't add `?? null` / `?? false` / `?? []` coercions unless the upstream genuinely returns `undefined`
 
 ### Existing Context Hierarchy
 - `ChatProvider` (`contexts/ChatContext.tsx`) — static chat metadata: `chatId`, `sandboxId`, `fileStructure`, `customAgents`, `customSlashCommands`, `customPrompts`
@@ -160,28 +169,28 @@
 - Before removing a UI element, check whether it serves a responsive/functional role beyond its visual purpose — icons often double as compact-mode fallbacks (`compactOnMobile`); labels may be the only visible element at some breakpoints
 
 ### File Placement
-- When extracting non-component code (contexts, utils, hooks) from a component file, place it in the canonical folder (`contexts/`, `utils/`, `hooks/`) — don't leave it next to the component
+- When extracting non-component code (contexts, utils, hooks) from a component file, place it in the canonical folder (`contexts/`, `utils/`, `hooks/`)
 - `components/chat/tools/` is exclusively for tool components (one per tool type) — helper modals/dialogs/detail views belong in `components/chat/` or a relevant feature folder
-- Shared UI used by 2+ feature areas belongs in `components/ui/shared/` — don't leave it in a feature folder just because the first consumer lives there
+- Shared UI used by 2+ feature areas belongs in `components/ui/shared/`
 
 ### Event Handler Signatures
 - Never pass a callback directly to `onClick` (or similar) when it expects domain-typed args — wrap in an arrow: `onClick={() => handler(value)}`, not `onClick={handler}` (React passes the event as the first arg)
 
 ### useEffect Discipline
-- Never place hooks (`useState`, `useCallback`, `useMemo`, `useEffect`) after conditional early returns — hooks must be called in the same order every render
+- Never place hooks (`useState`, `useCallback`, `useMemo`, `useEffect`) after conditional early returns
 - Never call `useEffect` directly for mount-only effects — use `useMountEffect()` from `hooks/useMountEffect.ts`
 - Never use `useEffect` to derive state from other state/props — use inline computation or `useMemo`; `useEffect(() => setX(f(y)), [y])` causes an extra render cycle
-- When state must reset on a prop/ID change, use a ref-based render check: `const prevRef = useRef(prop); if (prevRef.current !== prop) { prevRef.current = prop; setState(initial); }` — runs synchronously, avoids double render
-- Distinguish "derived state" from "form state init" — if local state is a copy of server data the user then edits independently (secrets form, settings form), syncing via `useEffect` on query data change is correct; don't convert these to inline derivation
-- `useEffect` cleanup closures must not rely on hook-scoped utilities that close over the current entity ID (e.g., `updateMessageInCache` scoped to the rendered `chatId`) when cleanup may serve sessions from a different entity — use refs or the underlying API (e.g., `queryClient.setQueryData` with `session.chatId`)
+- When state must reset on a prop/ID change, use a ref-based render check: `const prevRef = useRef(prop); if (prevRef.current !== prop) { prevRef.current = prop; setState(initial); }`
+- Distinguish "derived state" from "form state init" — if local state is a copy of server data the user then edits independently (secrets/settings forms), syncing via `useEffect` on query data change is correct
+- `useEffect` cleanup closures must not rely on hook-scoped utilities that close over the current entity ID when cleanup may serve sessions from a different entity — use refs or the underlying API (e.g., `queryClient.setQueryData` with `session.chatId`)
 
 ### Component Variants
 - Create explicit variant components instead of one with many boolean modes (e.g., `ThreadComposer`, `EditComposer` instead of `<Composer isThread isEditing />`)
-- Use `children` for composing static structure; render props only when the parent needs data back from the child (e.g., `renderItem` in lists)
+- Use `children` for composing static structure; render props only when the parent needs data back from the child
 
 ### Action Gating
-- When a React Query uses `placeholderData` / `keepPreviousData`, gate destructive actions derived from that data on `!isPlaceholderData` so they can't fire against rows from a previous query
-- Gate action buttons on backend capability, not UI rendering state — a bulk action that doesn't depend on per-row parsing shouldn't disappear when the list fails to parse; hide only the affordances that genuinely require rendered rows
+- When a React Query uses `placeholderData` / `keepPreviousData`, gate destructive actions derived from that data on `!isPlaceholderData`
+- Gate action buttons on backend capability, not UI rendering state — hide only the affordances that genuinely require rendered rows
 
 ## Frontend Performance Conventions
 
@@ -190,25 +199,25 @@
 - Heavy libraries must use dynamic `import()`, never static: `xlsx`, `jszip`, `xterm`, `@monaco-editor/react`, `react-vnc`, `qrcode`, `dompurify`, `mermaid`
 - Heavy React components: `React.lazy()` + `<Suspense>` (e.g., Monaco in dialogs, VncScreen)
 - Heavy libraries used in hooks/effects: `await import('lib')` inside the async function
-- Audit `package.json` periodically for unused deps — remove any package with zero imports in `src/`
+- Audit `package.json` periodically for unused deps
 
 ### Async-to-Sync Migration Safety
-- When converting sync (useMemo/inline) to async (useEffect + useState with dynamic imports), clear the previous state at the top of the effect before async work — otherwise users see stale data while the new result loads
+- When converting sync (useMemo/inline) to async (useEffect + useState with dynamic imports), clear the previous state at the top of the effect before async work
 - Pattern: `useEffect(() => { setState(initial); if (!input) return; let cancelled = false; (async () => { ... })(); return () => { cancelled = true; }; }, [input])`
 
 ### Re-render Optimization
 - Zustand action selectors used only in callbacks: use `useStore.getState().action()` at the call site — don't subscribe via `useStore((s) => s.action)`
 - Don't wrap Zustand `set(...)` in `startTransition` inside store definitions — use synchronous `set`; `startTransition` belongs in components/hooks
-- Zustand selectors must return stable references — never create new objects/arrays/`Set`/`Map` inside the selector; subscribe to stable slices and derive with `useMemo`
+- Zustand selectors must return stable references — never create new objects/arrays/`Set`/`Map` inside the selector; derive with `useMemo`
 - Use `Set` for membership checks in render loops — `useMemo(() => new Set(arr), [arr])` + `.has()` instead of `.includes()`
 - Don't wrap trivial expressions in `useMemo` (e.g., `useMemo(() => x || [], [x])`) — use `x ?? []`
-- When query keys include optional dimensions (e.g., `cwd`), add a separate prefix key without the optional dimension for broad invalidation (e.g., `gitBranchesAll: (id) => ['sandbox', id, 'git-branches']` alongside `gitBranches: (id, cwd?) => ['sandbox', id, 'git-branches', cwd]`) — invalidation with `undefined` doesn't prefix-match real values
+- When query keys include optional dimensions (e.g., `cwd`), add a separate prefix key without the optional dimension for broad invalidation (e.g., `gitBranchesAll: (id) => ['sandbox', id, 'git-branches']`) — invalidation with `undefined` doesn't prefix-match real values
 - Hoist regex patterns to module-level constants — never create `RegExp` inside loops/frequently-called functions
 - Prefer single-pass `.reduce()` over chained `.filter().map()` in render paths
-- When reordering a function call earlier in a per-event hot path (e.g., stream envelope processing), gate it with the cheapest condition at the call site — don't pay call overhead for the 99% that would early-return
-- Keep `useEffect` for external system subscriptions and DOM side effects — keyboard shortcuts, resize observers, WebSocket lifecycle, scroll-into-view, focus management need post-render timing and cleanup; don't convert these to ref-based render checks
+- When reordering a function call earlier in a per-event hot path, gate it with the cheapest condition at the call site
+- Keep `useEffect` for external system subscriptions and DOM side effects (keyboard shortcuts, resize observers, WebSocket lifecycle, scroll-into-view, focus management) — don't convert these to ref-based render checks
 - When unifying components with variant-specific features, gate Zustand selectors to return a stable value for variants that don't use that state (e.g., `useStore((s) => needsFeature ? s.value : false)`)
-- When invalidating a React Query key built from an identifier (paths, IDs, slugs), verify the format matches consumers' — cwd-relative vs workspace-root-relative paths miss each other, especially in worktree/nested-cwd setups; when formats can diverge, invalidate a prefix key (e.g., `fileContentAll`)
+- When invalidating a React Query key built from an identifier, verify the format matches consumers' — cwd-relative vs workspace-root-relative paths miss each other; when formats can diverge, invalidate a prefix key (e.g., `fileContentAll`)
 
 ### Async Patterns
 - Use `Promise.all()` for independent async ops (e.g., multiple `queryClient.invalidateQueries()` calls)
@@ -219,7 +228,7 @@
 
 ### Design Philosophy
 - Fully monochrome — no brand/blue accent colors in structural UI
-- Clean, minimal, refined — subtle over visually heavy; every element should feel quiet and intentional
+- Clean, minimal, refined — subtle over visually heavy
 - When multiple visual approaches are viable (connector styles, layout, color), present visual mockups for selection before implementation
 
 ### Color Palette
@@ -231,14 +240,14 @@
 - Text tokens: `text-text-primary`, `text-text-secondary`, `text-text-tertiary`, `text-text-quaternary` — dark `text-text-dark-*`
 - **Never use `brand-*` for buttons, switches, highlights, focus rings, or structural elements** — UI is fully monochrome
 - Primary buttons: `bg-text-primary text-surface` / `dark:bg-text-dark-primary dark:text-surface-dark` (inverted text/surface)
-- Switches/toggles: `bg-text-primary` when checked, `bg-surface-tertiary` when unchecked
+- Switches/toggles: `bg-text-primary` checked, `bg-surface-tertiary` unchecked
 - Focus rings: `ring-text-quaternary/30` — never `ring-brand-*`
-- Search highlights: `bg-surface-active` / `dark:bg-surface-dark-hover` — never `bg-brand-*`
-- Selected/active states: `bg-surface-active` / `dark:bg-surface-dark-active` — never `bg-brand-*`
-- Semantic colors (`success`, `error`, `warning`, `info`) are for status indicators only, not layout; don't use `error-*` / `warning-*` / `success-*` for interactive button backgrounds
-- Every `dark:text-*` / `dark:bg-*` must have a corresponding light-mode class — never rely on inherited color for one mode while explicitly setting the other
+- Search highlights: `bg-surface-active` / `dark:bg-surface-dark-hover`
+- Selected/active states: `bg-surface-active` / `dark:bg-surface-dark-active`
+- Semantic colors (`success`, `error`, `warning`, `info`) are for status indicators only, not layout or interactive button backgrounds
+- Every `dark:text-*` / `dark:bg-*` must have a corresponding light-mode class
 - Use opacity sparingly for glassmorphism (`/50`, `/30`); white/black only as opacity overlays (`bg-white/5`, `bg-black/50`), never solid
-- Don't use opacity below `/30` for structural lines (connectors, tree branches, dividers) — use `/50` minimum or full opacity for elements that must stay visible
+- Don't use opacity below `/30` for structural lines (connectors, tree branches, dividers) — use `/50` minimum
 
 ### Typography
 - `text-xs` default, `text-sm` for primary inputs, `text-2xs` for meta/section headers, `text-lg` for dialog titles only — avoid `text-base`+ in dense UI
@@ -279,8 +288,8 @@
 
 ### Layout
 - Don't use absolute positioning for sibling layout — use flexbox (`flex`, `justify-between`, `gap-*`); reserve `absolute` for overlays, tooltips, dropdowns, decorative elements
-- When action buttons have variable-length or long labels, stack vertically (`flex-col`) at full width — horizontal rows break awkwardly with wrapped/uneven widths
-- When nesting child items under parents (e.g., sub-threads), always maintain visible indentation — don't align child text flush with parent; connector lines/visual cues supplement but indentation is the primary hierarchy signal
+- When action buttons have variable-length or long labels, stack vertically (`flex-col`) at full width
+- When nesting child items under parents (e.g., sub-threads), always maintain visible indentation — connector lines supplement but indentation is the primary hierarchy signal
 
 ## Code Review Guidelines
 
@@ -291,36 +300,21 @@
 - Dead code left behind by the change (unused imports, unreachable branches, orphaned constants)
 
 ### What to skip
-- Orphaned DB rows from unlikely failure paths — a stray empty message row is harmless in a single-user app; don't add delete-rollback logic
+- Orphaned DB rows from unlikely failure paths — a stray empty message row is harmless in a single-user app
 - Concurrency edge cases (double-submit, multi-tab races, overlapping requests) unless the task explicitly asks for concurrency hardening
-- Hypothetical compatibility mismatches when a natural fallback already handles the case — don't add pre-flight checks to detect/re-route
+- Hypothetical compatibility mismatches when a natural fallback already handles the case
 - State-restoration rollback for failure paths — log + best-effort recovery (re-queue) is sufficient
 
 ### Callback closure analysis
 - When reviewing React hooks, event handlers, or async stream callbacks, verify which render created the callback before concluding what props/state it closes over
 - Don't infer a closure bug from a helper being parameterized by the current prop/state value unless you've traced creation site, storage, and which instance is invoked later
 - Callbacks stored outside React render flow (refs, Zustand stores, event listeners, stream registries, service singletons) are snapshots of the render that created them — they don't track the currently visible screen or latest hook inputs
 - Before flagging cross-chat/cross-screen/cross-context state contamination, trace the full lifecycle: creation site, captured values, storage location, update path, invocation site
-- Prefer concrete lifecycle traces over static closure assumptions when hooks interact with long-lived stores, subscriptions, or external event sources
 
 ### Failure-path control flow
 - When reviewing error handling, trace the exact path an exception takes through `except`, `raise`, and `return` boundaries before concluding later code is affected
 - Don't flag success-path classification logic as buggy unless you've verified execution can still reach it after the failure
-- In async call chains, follow the failure across helper methods and outer handlers all the way to the final state write before reporting misclassification
-- Before raising a finding about status handling, verify which exact lines run next after the failure
+- In async call chains, follow the failure across helper methods and outer handlers all the way to the final state write
 
 ### Complexity test
 Ask: "If this fails, does the user lose data or get stuck?" If no (orphaned row, briefly stale UI), skip. If yes (queued message silently dropped, stream appears frozen), fix.
-
-## Verification
-
-- Don't run tests, lints, type checks, or similar verification commands unless explicitly asked
-
-## Completion Quality Gate
-
-- No dead code left behind — remove unused functions, exports, imports, constants, types, files, and stale wrappers in the same task
-- Every task includes a final dead-code sweep across touched areas and new files
-- Before finishing, verify new/modified paths:
-  - New symbols are referenced (or intentionally public and documented)
-  - Replaced symbols are removed and references updated
-- If something is intentionally left unused for compatibility, state that explicitly in the final summary
PATCH

echo "Gold patch applied."

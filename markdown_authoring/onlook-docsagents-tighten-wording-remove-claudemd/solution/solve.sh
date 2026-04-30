#!/usr/bin/env bash
set -euo pipefail

cd /workspace/onlook

# Idempotency guard
if grep -qF "- Create store instances with `useState(() => new Store())` for stability across" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,17 +1,144 @@
-# Repository Contribution Guidelines
+## Onlook Agents Guide
 
-This file contains instructions for automated agents interacting with the Onlook repository.
+Actionable rules for repo agents—keep diffs minimal, safe, token‑efficient.
 
-## Commit Requirements
-- Run `bun format` to ensure consistent formatting.
-- Run `bun lint` and `bun test` for any packages you modify. Tests may require running `bun install` first.
-- Use clear, descriptive commit messages.
+### Purpose & Scope
 
-## Pull Request Guidelines
-- Use `.github/pull_request_template.md` when creating PRs.
-- Link related issues using GitHub keywords like `closes #123`.
-- Provide a concise summary of the changes and any relevant testing steps.
+- Audience: automated coding agents working within this repository.
+- Goal: small, correct diffs aligned with the project’s architecture.
+- Non-goals: editing generated artifacts, lockfiles, or `node_modules`.
 
-## Additional Notes
-- Follow the [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [CONTRIBUTING.md](CONTRIBUTING.md) documents.
-- If tests fail due to missing dependencies or environment limitations, note this in the PR description.
+### Repo Map
+
+- Monorepo managed by Bun workspaces (see root `package.json`).
+- App: `apps/web/client` (Next.js App Router + TailwindCSS).
+- API routes: `apps/web/client/src/server/api/routers/*`, aggregated in
+  `apps/web/client/src/server/api/root.ts`.
+- Shared utilities: `packages/*` (e.g., `packages/utility`).
+
+### Stack & Runtimes
+
+- UI: Next.js App Router, TailwindCSS.
+- API: tRPC + Zod (`apps/web/client/src/server/api/*`).
+
+### Agent Priorities
+
+- Correctness first: minimal scope and targeted edits.
+- Respect client/server boundaries in App Router.
+- Prefer local patterns and existing abstractions; avoid one-off frameworks.
+- Do not modify build outputs, generated files, or lockfiles.
+- Use Bun for all scripts; do not introduce npm/yarn.
+- Avoid running the local dev server in automation contexts.
+- Respect type safety and
+
+### Next.js App Router
+
+- Default to Server Components. Add `use client` when using events,
+  state/effects, browser APIs, or client-only libs.
+- App structure: `apps/web/client/src/app/**` (`page.tsx`, `layout.tsx`,
+  `route.ts`).
+- Client providers live behind a client boundary (e.g.,
+  `apps/web/client/src/trpc/react.tsx`).
+- Example roots: `apps/web/client/src/app/layout.tsx` (RSC shell, providers
+  wired, scripts gated by env).
+- Components using `mobx-react-lite`'s `observer` must be client components
+  (include `use client`).
+
+### tRPC API
+
+- Routers live in `apps/web/client/src/server/api/routers/**` and must be
+  exported from `apps/web/client/src/server/api/root.ts`.
+- Use `publicProcedure`/`protectedProcedure` from
+  `apps/web/client/src/server/api/trpc.ts`; validate inputs with Zod.
+- Serialization handled by SuperJSON; return plain objects/arrays.
+- Client usage via `apps/web/client/src/trpc/react.tsx` (React Query + tRPC
+  links).
+
+### Auth & Supabase
+
+- Server-side client: `apps/web/client/src/utils/supabase/server.ts` (uses Next
+  headers/cookies). Use in server components, actions, and routes.
+- Browser client: `apps/web/client/src/utils/supabase/client/index.ts` for
+  client components.
+- Never pass server-only clients into client code.
+
+### Env & Config
+
+- Define/validate env vars in `apps/web/client/src/env.ts` via
+  `@t3-oss/env-nextjs`.
+- Expose browser vars with `NEXT_PUBLIC_*` and declare in the `client` schema.
+- Prefer `env` from `@/env`. In server-only helpers (e.g., base URL in
+  `src/trpc/helpers.ts`), read `process.env` only for deployment vars like
+  `VERCEL_URL`/`PORT`. Never use `process.env` in client code; in shared
+  modules, guard with `typeof window === 'undefined'`.
+- Import `./src/env` in `apps/web/client/next.config.ts` to enforce validation.
+
+### Imports & Paths
+
+- Use path aliases: `@/*` and `~/*` map to `apps/web/client/src/*` (see
+  `apps/web/client/tsconfig.json`).
+- Do not import server-only modules into client components. Limited exception:
+  editor modules that already use `path`; reuse only there. Never import
+  `process` in client code.
+- Split code by environment if needed (server file vs client file).
+
+### MobX + React Stores
+
+- Create store instances with `useState(() => new Store())` for stability across
+  renders.
+- Keep active store in `useRef`; clean up async with
+  `setTimeout(() => storeRef.current?.clear(), 0)` to avoid route-change races.
+- Avoid `useMemo` for store instances; React may drop memoized values leading to
+  data loss.
+- Avoid putting the store instance in effect deps if it loops; split concerns
+  (e.g., project vs branch).
+- `observer` components are client-only. Place one client boundary at the
+  feature entry; child observers need not include `use client` (e.g.,
+  `apps/web/client/src/app/project/[id]/_components/main.tsx`).
+- Example store: `apps/web/client/src/components/store/editor/engine.ts:1` (uses
+  `makeAutoObservable`).
+
+### Styling & UI
+
+- TailwindCSS-first styling; global styles are already imported in
+  `apps/web/client/src/app/layout.tsx`.
+- Prefer existing UI components from `@onlook/ui` and local patterns.
+- Preserve dark theme defaults via `ThemeProvider` usage in layout.
+
+### Internationalization
+
+- `next-intl` is configured; provider lives in
+  `apps/web/client/src/app/layout.tsx`.
+- Strings live in `apps/web/client/messages/*`. Add/modify keys there; avoid
+  hardcoded user-facing text.
+- Keep keys stable; prefer additions over breaking renames.
+
+### Common Pitfalls
+
+- Missing `use client` where needed (events/browser APIs) causes unbound events;
+  a single boundary at the feature root is sufficient.
+- New tRPC routers not exported in `src/server/api/root.ts` (endpoints
+  unreachable).
+- Env vars not typed/exposed in `src/env.ts` cause runtime/edge failures. Prefer
+  `env`; avoid new `process.env` reads in client code.
+- Importing server-only code into client components (bundling/runtime errors).
+  Note: `path` is already used in specific client code-editor modules; avoid
+  expanding Node API usage beyond those areas.
+- Bypassing i18n by hardcoding strings instead of using message files/hooks.
+- Avoid `useMemo` to create MobX stores (risk of lost references); avoid
+  synchronous cleanup on route change (race conditions).
+
+### Context Discipline (for Agents)
+
+- Search narrowly with ripgrep; open only files you need.
+- Read small sections; avoid `node_modules`, `.next`, large assets.
+- Propose minimal diffs aligned with existing conventions; avoid wide refactors.
+
+### Notes
+
+- Unit tests can be run with `bun test`
+- Run type checking with `bun run typecheck`
+- Apply database updates to local dev with `bun run db:push`
+- Refrain from running the dev server
+- DO NOT run `db:gen`. This is reserved for the maintainer.
+- DO NOT use any type unless necessary
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,52 +0,0 @@
-- This is a Bun workspace, only use bun, not npm
-- Unit tests can be run with `bun test`
-- Run type checking with `bun run typecheck`
-- Apply database updates to local dev with `bun run db:push`
-- Refrain from running the dev server
-
-## MobX + React Best Practices
-
-### Pattern for Provider Components with Observable Stores
-
-When creating React providers that manage MobX observable stores (like
-EditorEngine):
-
-**✅ DO:**
-
-- Use `useState(() => new Store())` for stable observable instances (MobX
-  recommended pattern)
-- Keep refs (`engineRef.current`) to avoid stale closures in effects
-- Use `setTimeout(() => store.clear(), 0)` for delayed cleanup to avoid race
-  conditions
-- Separate project changes from branch updates with proper dependency arrays
-
-**❌ DON'T:**
-
-- Use `useMemo` for observable references - React may randomly "forget" them
-  (data loss risk)
-- Clean up stores synchronously during navigation - causes "No branch selected"
-  errors
-- Include the store instance in effect dependency arrays if it causes infinite
-  loops
-
-### Example Pattern:
-
-```tsx
-const [store, setStore] = useState(() => new Store(props));
-const storeRef = useRef<Store | null>(store);
-
-useEffect(() => {
-    if (propChanged) {
-        setTimeout(() => storeRef.current?.clear(), 0); // Delayed cleanup
-        const newStore = new Store(newProps);
-        storeRef.current = newStore;
-        setStore(newStore);
-    }
-}, [propChanged]);
-
-useEffect(() => {
-    return () => setTimeout(() => storeRef.current?.clear(), 0);
-}, []);
-```
-
-This maintains MobX reactivity while preventing cleanup race conditions.
PATCH

echo "Gold patch applied."

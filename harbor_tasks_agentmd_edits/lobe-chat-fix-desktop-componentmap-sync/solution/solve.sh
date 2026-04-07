#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -q 'SettingsTabs.Stats' src/routes/\(main\)/settings/features/componentMap.desktop.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.agents/skills/code-review/SKILL.md b/.agents/skills/code-review/SKILL.md
index 1fb3a3ce38e..073240f0523 100644
--- a/.agents/skills/code-review/SKILL.md
+++ b/.agents/skills/code-review/SKILL.md
@@ -37,6 +37,10 @@ description: 'Code review checklist for LobeHub. Use when reviewing PRs, diffs,
 - Keys added to `src/locales/default/{namespace}.ts` with `{feature}.{context}.{action|status}` naming
 - For PRs: `locales/` translations for all languages updated (`pnpm i18n`)

+### SPA / routing
+
+- **`desktopRouter` pair:** If the diff touches `src/spa/router/desktopRouter.config.tsx`, does it also update `src/spa/router/desktopRouter.config.desktop.tsx` with the same route paths and nesting? Single-file edits often cause drift and blank screens.
+
 ### Reuse

 - Newly written code duplicates existing utilities in `packages/utils` or shared modules?
diff --git a/.agents/skills/react/SKILL.md b/.agents/skills/react/SKILL.md
index ecb94901908..4aadcdd667b 100644
--- a/.agents/skills/react/SKILL.md
+++ b/.agents/skills/react/SKILL.md
@@ -32,15 +32,28 @@ Hybrid routing: Next.js App Router (static pages) + React Router DOM (main SPA).
 | Route Type         | Use Case                          | Implementation               |
 | ------------------ | --------------------------------- | ---------------------------- |
 | Next.js App Router | Auth pages (login, signup, oauth) | `src/app/[variants]/(auth)/` |
-| React Router DOM   | Main SPA (chat, settings)         | `desktopRouter.config.tsx`   |
+| React Router DOM   | Main SPA (chat, settings)         | `desktopRouter.config.tsx` + `desktopRouter.config.desktop.tsx` (must match) |

 ### Key Files

 - Entry: `src/spa/entry.web.tsx` (web), `src/spa/entry.mobile.tsx`, `src/spa/entry.desktop.tsx`
-- Desktop router: `src/spa/router/desktopRouter.config.tsx`
+- Desktop router (pair — **always edit both** when changing routes): `src/spa/router/desktopRouter.config.tsx` (dynamic imports) and `src/spa/router/desktopRouter.config.desktop.tsx` (sync imports). Drift can cause unregistered routes / blank screen.
 - Mobile router: `src/spa/router/mobileRouter.config.tsx`
 - Router utilities: `src/utils/router.tsx`

+### `.desktop.{ts,tsx}` File Sync Rule
+
+**CRITICAL**: Some files have a `.desktop.ts(x)` variant that Electron uses instead of the base file. When editing a base file, **always check** if a `.desktop` counterpart exists and update it in sync. Drift causes blank pages or missing features in Electron.
+
+Known pairs that must stay in sync:
+
+| Base file (web, dynamic imports) | Desktop file (Electron, sync imports) |
+| --- | --- |
+| `src/spa/router/desktopRouter.config.tsx` | `src/spa/router/desktopRouter.config.desktop.tsx` |
+| `src/routes/(main)/settings/features/componentMap.ts` | `src/routes/(main)/settings/features/componentMap.desktop.ts` |
+
+**How to check**: After editing any `.ts` / `.tsx` file, run `Glob` for `<filename>.desktop.{ts,tsx}` in the same directory. If a match exists, update it with the equivalent sync-import change.

 ### Router Utilities

diff --git a/.agents/skills/spa-routes/SKILL.md b/.agents/skills/spa-routes/SKILL.md
index 0cd55f37108..dbc6a653e37 100644
--- a/.agents/skills/spa-routes/SKILL.md
+++ b/.agents/skills/spa-routes/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: spa-routes
-description: SPA route and feature structure. Use when adding or modifying SPA routes in src/routes, defining new route segments, or moving route logic into src/features. Covers how to keep routes thin and how to divide files between routes and features.
+description: MUST use when editing src/routes/ segments, src/spa/router/desktopRouter.config.tsx or desktopRouter.config.desktop.tsx (always change both together), mobileRouter.config.tsx, or when moving UI/logic between routes and src/features/.
 ---

@@ -13,6 +13,8 @@ SPA structure:

 This project uses a **roots vs features** split: `src/routes/` only holds page segments; business logic and UI live in `src/features/` by domain.

+**Agent constraint — desktop router parity:** Edits to the desktop route tree must update **both** `src/spa/router/desktopRouter.config.tsx` and `src/spa/router/desktopRouter.config.desktop.tsx` in the same change (same paths, nesting, index routes, and segment registration). Updating only one causes drift; the missing tree can fail to register routes and surface as a **blank screen** or broken navigation on the affected build.
+
 ## When to Use This Skill

@@ -73,8 +75,21 @@ Each feature should:
    - Layout: `export { default } from '@/features/MyFeature/MyLayout'` or compose a few feature components + `<Outlet />`.
    - Page: import from `@/features/MyFeature` (or a specific subpath) and render; no business logic in the route file.

-5. **Register the route**
-   - Add the segment to `src/spa/router/desktopRouter.config.tsx` (or the right router config) with `dynamicElement` / `dynamicLayout` pointing at the new route paths (e.g. `@/routes/(main)/my-feature`).
+5. **Register the route (desktop — two files, always)**
+   - **`desktopRouter.config.tsx`:** Add the segment with `dynamicElement` / `dynamicLayout` pointing at route modules (e.g. `@/routes/(main)/my-feature`).
+   - **`desktopRouter.config.desktop.tsx`:** Mirror the **same** `RouteObject` shape: identical `path` / `index` / parent-child structure. Use the static imports and elements already used in that file (see neighboring routes). Do **not** register in only one of these files.
+   - **Mobile-only flows:** use `mobileRouter.config.tsx` instead (no need to duplicate into the desktop pair unless the route truly exists on both).
+
+---
+
+## 3a. Desktop router pair (`desktopRouter.config` x 2)
+
+| File | Role |
+|------|------|
+| `desktopRouter.config.tsx` | Dynamic imports via `dynamicElement` / `dynamicLayout` — code-splitting; used by `entry.web.tsx` and `entry.desktop.tsx`. |
+| `desktopRouter.config.desktop.tsx` | Same route tree with **synchronous** imports — kept for Electron / local parity and predictable bundling. |
+
+Anything that changes the tree (new segment, renamed `path`, moved layout, new child route) must be reflected in **both** files in one PR or commit. Remove routes from both when deleting.

 ---

diff --git a/src/routes/(main)/settings/features/componentMap.desktop.ts b/src/routes/(main)/settings/features/componentMap.desktop.ts
index 57dee35960f..9cdeb1c0a21 100644
--- a/src/routes/(main)/settings/features/componentMap.desktop.ts
+++ b/src/routes/(main)/settings/features/componentMap.desktop.ts
@@ -9,6 +9,7 @@ import About from '../about';
 import Advanced from '../advanced';
 import APIKey from '../apikey';
 import Appearance from '../appearance';
+import Creds from '../creds';
 import Hotkey from '../hotkey';
 import Memory from '../memory';
 import Profile from '../profile';
@@ -17,6 +18,7 @@ import Proxy from '../proxy';
 import Security from '../security';
 import ServiceModel from '../service-model';
 import Skill from '../skill';
+import Stats from '../stats';
 import Storage from '../storage';
 import SystemTools from '../system-tools';

@@ -33,8 +35,10 @@ export const componentMap = {
   [SettingsTabs.Storage]: Storage,
   // Profile related tabs
   [SettingsTabs.Profile]: Profile,
+  [SettingsTabs.Stats]: Stats,
   [SettingsTabs.Usage]: Usage,
   [SettingsTabs.APIKey]: APIKey,
+  [SettingsTabs.Creds]: Creds,
   [SettingsTabs.Security]: Security,
   [SettingsTabs.Skill]: Skill,

diff --git a/src/spa/router/desktopRouter.config.desktop.tsx b/src/spa/router/desktopRouter.config.desktop.tsx
index c0bf10c2557..38fd358a78f 100644
--- a/src/spa/router/desktopRouter.config.desktop.tsx
+++ b/src/spa/router/desktopRouter.config.desktop.tsx
@@ -462,3 +462,10 @@ desktopRoutes.push({
   errorElement: <ErrorBoundary resetPath="/" />,
   path: '/desktop-onboarding',
 });
+
+// Web onboarding aliases redirect to the desktop-specific onboarding flow.
+desktopRoutes.push({
+  element: redirectElement('/desktop-onboarding'),
+  errorElement: <ErrorBoundary resetPath="/" />,
+  path: '/onboarding',
+});

PATCH

echo "Patch applied successfully."

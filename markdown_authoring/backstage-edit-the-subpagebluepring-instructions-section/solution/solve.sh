#!/usr/bin/env bash
set -euo pipefail

cd /workspace/backstage

# Idempotency guard
if grep -qF "Old frontend plugins often use React Router `<Route>` trees inside a router comp" "docs/.well-known/skills/plugin-full-frontend-system-migration/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/docs/.well-known/skills/plugin-full-frontend-system-migration/SKILL.md b/docs/.well-known/skills/plugin-full-frontend-system-migration/SKILL.md
@@ -272,7 +272,37 @@ export const myPage = PageBlueprint.make({
 
 ## Step 5: Replace Internal Routing with Sub-Pages
 
-This is one of the biggest changes in a full migration. Old plugins often use React Router `<Route>` trees inside a router component to handle internal navigation. The new system replaces this with `SubPageBlueprint` for tabbed sub-pages.
+Old frontend plugins often use React Router `<Route>` trees inside a router component to handle internal navigation. Before migrating, determine which routing pattern fits the plugin.
+
+### Decide Which Routing Pattern to Use
+
+Not all internal routing maps to tabs. Read the plugin's existing router component and ask the user:
+
+> "Does your plugin use top-level tabs that users navigate between via a header (e.g. Overview / Settings)? Or does it use detail/drill-down routes (e.g. `/my-plugin/items/:id`)?"
+
+Use `SubPageBlueprint` when:
+
+- The sub-routes represent top-level tabs/sections of the plugin
+- Users navigate between them via the header
+
+Keep internal routing within a `PageBlueprint` `loader` when:
+
+- Routes are detail/drill-down pages (e.g. `/my-plugin/items/:id`)
+- The routing is deeply nested or dynamic
+
+**If the plugin uses drill-down routing only**, use a `PageBlueprint` with a `loader` that handles its own `<Routes>` and skip the rest of this step:
+
+```tsx
+export const myPage = PageBlueprint.make({
+  params: {
+    path: '/my-plugin',
+    routeRef: rootRouteRef,
+    loader: () => import('./components/Router').then(m => <m.MyPluginRouter />),
+  },
+});
+```
+
+**If the plugin uses top-level tabs**, continue with the `SubPageBlueprint` migration below.
 
 ### Old Pattern: Internal Router
 
@@ -349,30 +379,6 @@ How this works:
 
 If the sub-page content needs padding, use `Container` from `@backstage/ui` as a wrapper inside the component.
 
-### When NOT to Use Sub-Pages
-
-Not all internal routing maps to tabs. Use `SubPageBlueprint` when:
-
-- The sub-routes represent top-level tabs/sections of the plugin
-- Users navigate between them via the header
-
-Keep internal routing within a `PageBlueprint` `loader` when:
-
-- Routes are detail/drill-down pages (e.g. `/my-plugin/items/:id`)
-- The routing is deeply nested or dynamic
-
-In those cases, use a `PageBlueprint` **with** a `loader` that handles its own `Routes`:
-
-```tsx
-export const myPage = PageBlueprint.make({
-  params: {
-    path: '/my-plugin',
-    routeRef: rootRouteRef,
-    loader: () => import('./components/Router').then(m => <m.MyPluginRouter />),
-  },
-});
-```
-
 ## Step 6: Update Hooks and Imports
 
 Replace all `@backstage/core-plugin-api` imports with `@backstage/frontend-plugin-api`:
PATCH

echo "Gold patch applied."

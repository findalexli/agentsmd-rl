#!/bin/bash
set -e

cd /workspace/router

# Idempotency check: only apply patch if the fix is not already present
if ! grep -q 'import.meta.hot.data ??= {}' packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts 2>/dev/null; then
    # Apply the gold patch for the main fix
    git apply --ignore-whitespace <<'PATCH'
diff --git a/packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts b/packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts
index 5146202ad31..af05d48b31c 100644
--- a/packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts
+++ b/packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts
@@ -15,6 +15,7 @@ const buildStableSplitComponentStatements = template.statements(
   `
     const %%stableComponentIdent%% = import.meta.hot?.data?.[%%hotDataKey%%] ?? %%lazyRouteComponentIdent%%(%%localImporterIdent%%, %%exporterIdent%%)
     if (import.meta.hot) {
+      import.meta.hot.data ??= {}
       import.meta.hot.data[%%hotDataKey%%] = %%stableComponentIdent%%
     }
   `,
PATCH

    # Apply the snapshot updates
    git apply --ignore-whitespace <<'PATCH'
diff --git a/packages/router-plugin/tests/add-hmr/snapshots/react/arrow-function@true.tsx b/packages/router-plugin/tests/add-hmr/snapshots/react/arrow-function@true.tsx
index 17262ea127c..eb4d0cde419 100644
--- a/packages/router-plugin/tests/add-hmr/snapshots/react/arrow-function@true.tsx
+++ b/packages/router-plugin/tests/add-hmr/snapshots/react/arrow-function@true.tsx
@@ -5,6 +5,7 @@ import { createFileRoute } from '@tanstack/react-router';
 import { fetchPosts } from '../posts';
 const TSRSplitComponent = import.meta.hot?.data?.["tsr-split-component:component"] ?? lazyRouteComponent($$splitComponentImporter, "component");
 if (import.meta.hot) {
+  import.meta.hot.data ??= {};
   import.meta.hot.data["tsr-split-component:component"] = TSRSplitComponent;
 }
 export const Route = createFileRoute('/posts')({
diff --git a/packages/router-plugin/tests/add-hmr/snapshots/react/function-declaration@true.tsx b/packages/router-plugin/tests/add-hmr/snapshots/react/function-declaration@true.tsx
index 006868554a2..f8199dcd85d 100644
--- a/packages/router-plugin/tests/add-hmr/snapshots/react/function-declaration@true.tsx
+++ b/packages/router-plugin/tests/add-hmr/snapshots/react/function-declaration@true.tsx
@@ -5,6 +5,7 @@ import { createFileRoute } from '@tanstack/react-router';
 import { fetchPosts } from '../posts';
 const TSRSplitComponent = import.meta.hot?.data?.["tsr-split-component:component"] ?? lazyRouteComponent($$splitComponentImporter, "component");
 if (import.meta.hot) {
+  import.meta.hot.data ??= {};
   import.meta.hot.data["tsr-split-component:component"] = TSRSplitComponent;
 }
 export const Route = createFileRoute('/posts')({
diff --git a/packages/router-plugin/tests/add-hmr/snapshots/react/multi-component@true.tsx b/packages/router-plugin/tests/add-hmr/snapshots/react/multi-component@true.tsx
index df4236c39ea..06d6d353799 100644
--- a/packages/router-plugin/tests/add-hmr/snapshots/react/multi-component@true.tsx
+++ b/packages/router-plugin/tests/add-hmr/snapshots/react/multi-component@true.tsx
@@ -6,10 +6,12 @@ import { createFileRoute } from '@tanstack/react-router';
 import { fetchPosts } from '../posts';
 const TSRSplitComponent = import.meta.hot?.data?.["tsr-split-component:component"] ?? lazyRouteComponent($$splitComponentImporter, "component");
 if (import.meta.hot) {
+  import.meta.hot.data ??= {};
   import.meta.hot.data["tsr-split-component:component"] = TSRSplitComponent;
 }
 const TSRSplitErrorComponent = import.meta.hot?.data?.["tsr-split-component:errorComponent"] ?? lazyRouteComponent($$splitErrorComponentImporter, "errorComponent");
 if (import.meta.hot) {
+  import.meta.hot.data ??= {};
   import.meta.hot.data["tsr-split-component:errorComponent"] = TSRSplitErrorComponent;
 }
 export const Route = createFileRoute('/posts')({
diff --git a/packages/router-plugin/tests/add-hmr/snapshots/react/string-literal-keys@true.tsx b/packages/router-plugin/tests/add-hmr/snapshots/react/string-literal-keys@true.tsx
index 3c45803585f..f62d1a28316 100644
--- a/packages/router-plugin/tests/add-hmr/snapshots/react/string-literal-keys@true.tsx
+++ b/packages/router-plugin/tests/add-hmr/snapshots/react/string-literal-keys@true.tsx
@@ -6,10 +6,12 @@ import { createFileRoute } from '@tanstack/react-router';
 import { fetchPosts } from '../posts';
 const TSRSplitComponent = import.meta.hot?.data?.["tsr-split-component:component"] ?? lazyRouteComponent($$splitComponentImporter, "component");
 if (import.meta.hot) {
+  import.meta.hot.data ??= {};
   import.meta.hot.data["tsr-split-component:component"] = TSRSplitComponent;
 }
 const TSRSplitErrorComponent = import.meta.hot?.data?.["tsr-split-component:errorComponent"] ?? lazyRouteComponent($$splitErrorComponentImporter, "errorComponent");
 if (import.meta.hot) {
+  import.meta.hot.data ??= {};
   import.meta.hot.data["tsr-split-component:errorComponent"] = TSRSplitErrorComponent;
 }
 export const Route = createFileRoute('/posts')({
PATCH

    echo "Patch applied successfully"
else
    echo "Fix already applied, skipping patch"
fi

# Rebuild the router-plugin package
pnpm nx run @tanstack/router-plugin:build

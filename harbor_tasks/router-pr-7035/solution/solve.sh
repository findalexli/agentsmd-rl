#!/bin/bash
set -e

cd /workspace/router

# Idempotency check - if the fix is already applied, skip
if grep -q '"rootDir": "./src/default-entry"' packages/react-start/tsconfig.server-entry.json 2>/dev/null; then
    echo "Fix already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/react-start/tsconfig.server-entry.json b/packages/react-start/tsconfig.server-entry.json
new file mode 100644
index 00000000000..fff45a1ed33
--- /dev/null
+++ b/packages/react-start/tsconfig.server-entry.json
@@ -0,0 +1,7 @@
+{
+  "extends": "./tsconfig.json",
+  "compilerOptions": {
+    "rootDir": "./src/default-entry"
+  },
+  "include": ["src/default-entry"]
+}
diff --git a/packages/react-start/vite.config.server-entry.ts b/packages/react-start/vite.config.server-entry.ts
index 819215514d6..8b64d36cc72 100644
--- a/packages/react-start/vite.config.server-entry.ts
+++ b/packages/react-start/vite.config.server-entry.ts
@@ -1,6 +1,7 @@
 import { tanstackViteConfig } from '@tanstack/vite-config'

 export default tanstackViteConfig({
+  tsconfigPath: './tsconfig.server-entry.json',
   srcDir: './src/default-entry',
   exclude: ['./src/default-entry/client.tsx'],
   entry: ['./src/default-entry/server.ts'],
diff --git a/packages/solid-start/tsconfig.server-entry.json b/packages/solid-start/tsconfig.server-entry.json
new file mode 100644
index 00000000000..fff45a1ed33
--- /dev/null
+++ b/packages/solid-start/tsconfig.server-entry.json
@@ -0,0 +1,7 @@
+{
+  "extends": "./tsconfig.json",
+  "compilerOptions": {
+    "rootDir": "./src/default-entry"
+  },
+  "include": ["src/default-entry"]
+}
diff --git a/packages/solid-start/vite.config.server-entry.ts b/packages/solid-start/vite.config.server-entry.ts
index 2b9d8249bce..6ba821babd9 100644
--- a/packages/solid-start/vite.config.server-entry.ts
+++ b/packages/solid-start/vite.config.server-entry.ts
@@ -1,6 +1,7 @@
 import { tanstackViteConfig } from '@tanstack/vite-config'

 export default tanstackViteConfig({
+  tsconfigPath: './tsconfig.server-entry.json',
   srcDir: './src/default-entry',
   exclude: ['./src/default-entry/client.tsx'],
   entry: ['./src/default-entry/server.ts'],
diff --git a/packages/vue-start/tsconfig.server-entry.json b/packages/vue-start/tsconfig.server-entry.json
new file mode 100644
index 00000000000..fff45a1ed33
--- /dev/null
+++ b/packages/vue-start/tsconfig.server-entry.json
@@ -0,0 +1,7 @@
+{
+  "extends": "./tsconfig.json",
+  "compilerOptions": {
+    "rootDir": "./src/default-entry"
+  },
+  "include": ["src/default-entry"]
+}
diff --git a/packages/vue-start/vite.config.server-entry.ts b/packages/vue-start/vite.config.server-entry.ts
index c75bfa1da8b..26606ca6649 100644
--- a/packages/vue-start/vite.config.server-entry.ts
+++ b/packages/vue-start/vite.config.server-entry.ts
@@ -9,6 +9,7 @@ const config = defineConfig({
 export default mergeConfig(
   config,
   tanstackViteConfig({
+    tsconfigPath: './tsconfig.server-entry.json',
     srcDir: './src/default-entry',
     exclude: ['./src/default-entry/client.tsx'],
     entry: ['./src/default-entry/server.ts'],
PATCH

echo "Patch applied successfully."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nextjs

# Idempotency: skip if patch already applied
if grep -q '"build-all": "turbo run build build-native-auto' package.json 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply --ignore-whitespace --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index d00760084ff7..1aa08af4ee1f 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -58,9 +58,12 @@ Before editing or creating files in any subdirectory (e.g., `packages/*`, `crate
 # Build the Next.js package
 pnpm --filter=next build

-# Build everything
+# Build all JS code
 pnpm build

+# Build all JS and Rust code
+pnpm build-all
+
 # Run specific task
 pnpm --filter=next exec taskr <task>
 ```
@@ -91,13 +94,13 @@ NEXT_SKIP_ISOLATE=1 NEXT_TEST_MODE=dev pnpm testonly test/path/to/test.ts

 **For type errors only:** Use `pnpm --filter=next types` (~10s) instead of `pnpm --filter=next build` (~60s).

-After the workspace is bootstrapped, prefer `pnpm --filter=next build` when edits are limited to core Next.js files. Use full `pnpm build` for branch switches/bootstrap, before CI push, or when changes span multiple packages.
+After the workspace is bootstrapped, prefer `pnpm --filter=next build` when edits are limited to core Next.js files. Use full `pnpm build-all` for branch switches/bootstrap, before CI push, or when changes span multiple packages.

 **Always run a full bootstrap build after switching branches:**

 ```bash
 git checkout <branch>
-pnpm build   # Sets up outputs for dependent packages (Turborepo dedupes if unchanged)
+pnpm build-all   # Sets up outputs for dependent packages (Turborepo dedupes if unchanged)
 ```

 **When NOT to use NEXT_SKIP_ISOLATE:** Drop it when testing module resolution changes (new require() paths, new exports from entry-base.ts, edge route imports). Without isolation, the test uses local dist/ directly, hiding resolution failures that occur when Next.js is packed as a real npm package.
@@ -326,7 +329,7 @@ Use skills for conditional, deep workflows. Keep baseline iteration/build/test p

 **Build & test output:**

-- Capture to file once, then analyze: `pnpm build 2>&1 | tee /tmp/build.log`
+- Capture to file once, then analyze: e.g. `pnpm build 2>&1 | tee /tmp/build.log`
 - Don't re-run the same test command without code changes; re-analyze saved output instead

 **Batch edits before building:**
@@ -365,9 +368,9 @@ npx eslint --config eslint.config.mjs --fix <files>

 When running Next.js integration tests, you must rebuild if source files have changed:

-- **First run after branch switch/bootstrap (or if unsure)?** → `pnpm build`
+- **First run after branch switch/bootstrap (or if unsure)?** → `pnpm build-all`
 - **Edited only core Next.js files (`packages/next/**`) after bootstrap?** → `pnpm --filter=next build`
-- **Edited Next.js code or Turbopack (Rust)?** → `pnpm build`
+- **Edited Next.js code or Turbopack (Rust)?** → `pnpm build-all`

 ## Development Anti-Patterns

diff --git a/package.json b/package.json
index 90aec1deb8bd..bbae9bcedebf 100644
--- a/package.json
+++ b/package.json
@@ -10,6 +10,7 @@
     "new-test": "turbo gen test",
     "clean": "lerna clean -y && lerna run clean && lerna exec 'node ../../scripts/rm.mjs dist'",
     "build": "turbo run build --remote-cache-timeout 60 --summarize true",
+    "build-all": "turbo run build build-native-auto --remote-cache-timeout 60 --summarize true",
     "lerna": "lerna",
     "dev": "turbo run dev --parallel --filter=\"!@next/bundle-analyzer-ui\"",
     "bench:render-pipeline": "tsx bench/render-pipeline/benchmark.ts",
diff --git a/packages/next-swc/package.json b/packages/next-swc/package.json
index 47d786afd74c..e421775e8b71 100644
--- a/packages/next-swc/package.json
+++ b/packages/next-swc/package.json
@@ -6,7 +6,7 @@
     "native/"
   ],
   "scripts": {
-    "build": "node maybe-build-native.mjs",
+    "build-native-auto": "node maybe-build-native.mjs",
     "clean": "node ../../scripts/rm.mjs native",
     "build-native": "napi build --platform -p next-napi-bindings --cargo-cwd ../../ --cargo-name next_napi_bindings --features plugin,image-extended --js false native",
     "build-native-release": "napi build --platform -p next-napi-bindings --cargo-cwd ../../ --cargo-name next_napi_bindings --release --features plugin,image-extended,tracing/release_max_level_trace --js false native",
diff --git a/packages/next-swc/turbo.json b/packages/next-swc/turbo.jsonc
similarity index 78%
rename from packages/next-swc/turbo.json
rename to packages/next-swc/turbo.jsonc
index 054741d51de9..546655503ea7 100644
--- a/packages/next-swc/turbo.json
+++ b/packages/next-swc/turbo.jsonc
@@ -2,7 +2,10 @@
   "$schema": "https://turborepo.org/schema.json",
   "extends": ["//"],
   "tasks": {
-    "build": {
+    // "auto" is used by the workspace `pnpm build-all` script. It checks to see
+    // if there's already an up-to-date precompiled version of turbopack
+    // available before performing the build.
+    "build-native-auto": {
       "inputs": [
         "../../.cargo/**",
         "../../crates/**",
@@ -11,14 +14,14 @@
         "../../Cargo.toml",
         "../../Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
+        "../../rust-toolchain.toml",
       ],
       "env": ["CI"],
       "outputs": [
         "native/*.node",
         "native/index.d.ts",
-        "../../packages/next/src/build/swc/generated-native.d.ts"
-      ]
+        "../../packages/next/src/build/swc/generated-native.d.ts",
+      ],
     },
     "build-native": {
       "inputs": [
@@ -29,10 +32,10 @@
         "../../Cargo.toml",
         "../../Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
+        "../../rust-toolchain.toml",
       ],
       "env": ["CI"],
-      "outputs": ["native/*.node", "native/index.d.ts"]
+      "outputs": ["native/*.node", "native/index.d.ts"],
     },
     "build-native-release": {
       "inputs": [
@@ -43,10 +46,10 @@
         "../../**/Cargo.toml",
         "../../**/Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
+        "../../rust-toolchain.toml",
       ],
       "env": ["CI"],
-      "outputs": ["native/*.node", "native/index.d.ts"]
+      "outputs": ["native/*.node", "native/index.d.ts"],
     },
     "build-native-release-with-assertions": {
       "inputs": [
@@ -57,10 +60,10 @@
         "../../**/Cargo.toml",
         "../../**/Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
+        "../../rust-toolchain.toml",
       ],
       "env": ["CI"],
-      "outputs": ["native/*.node", "native/index.d.ts"]
+      "outputs": ["native/*.node", "native/index.d.ts"],
     },
     "build-native-no-plugin": {
       "inputs": [
@@ -71,10 +74,10 @@
         "../../**/Cargo.toml",
         "../../**/Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
+        "../../rust-toolchain.toml",
       ],
       "env": ["CI"],
-      "outputs": ["native/*.node", "native/index.d.ts"]
+      "outputs": ["native/*.node", "native/index.d.ts"],
     },
     "build-native-no-plugin-release": {
       "inputs": [
@@ -85,10 +88,10 @@
         "../../**/Cargo.toml",
         "../../**/Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
+        "../../rust-toolchain.toml",
       ],
       "env": ["CI"],
-      "outputs": ["native/*.node", "native/index.d.ts"]
+      "outputs": ["native/*.node", "native/index.d.ts"],
     },
     "build-wasm": {
       "inputs": [
@@ -99,10 +102,10 @@
         "../../**/Cargo.toml",
         "../../**/Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
+        "../../rust-toolchain.toml",
       ],
       "env": ["CI"],
-      "outputs": ["../../crates/wasm/pkg/*"]
+      "outputs": ["../../crates/wasm/pkg/*"],
     },
     "build-native-wasi": {
       "inputs": [
@@ -113,10 +116,10 @@
         "../../**/Cargo.toml",
         "../../**/Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
+        "../../rust-toolchain.toml",
       ],
       "env": ["CI"],
-      "outputs": ["native/*"]
+      "outputs": ["native/*"],
     },
     "cache-build-native": {
       "inputs": [
@@ -127,13 +130,13 @@
         "../../**/Cargo.toml",
         "../../**/Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
+        "../../rust-toolchain.toml",
       ],
       "env": ["CI"],
-      "outputs": ["native/*.node", "native/index.d.ts"]
+      "outputs": ["native/*.node", "native/index.d.ts"],
     },
     "rust-check": {
-      "dependsOn": ["rust-check-fmt", "rust-check-clippy", "rust-check-napi"]
+      "dependsOn": ["rust-check-fmt", "rust-check-clippy", "rust-check-napi"],
     },
     "rust-check-fmt": {
       "inputs": [
@@ -143,9 +146,9 @@
         "../../**/Cargo.toml",
         "../../**/Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
+        "../../rust-toolchain.toml",
       ],
-      "cache": false
+      "cache": false,
     },
     "rust-check-clippy": {
       "inputs": [
@@ -155,8 +158,8 @@
         "../../**/Cargo.toml",
         "../../**/Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
-      ]
+        "../../rust-toolchain.toml",
+      ],
     },
     "rust-check-napi": {
       "inputs": [
@@ -166,8 +169,8 @@
         "../../**/Cargo.toml",
         "../../**/Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
-      ]
+        "../../rust-toolchain.toml",
+      ],
     },
     "test-cargo-unit": {
       "inputs": [
@@ -177,8 +180,8 @@
         "../../**/Cargo.toml",
         "../../**/Cargo.lock",
         "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml"
-      ]
-    }
-  }
+        "../../rust-toolchain.toml",
+      ],
+    },
+  },
 }
PATCH

echo "Solve complete."

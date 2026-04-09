#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'rust-fingerprint' packages/next-swc/turbo.jsonc 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next-swc/package.json b/packages/next-swc/package.json
index 376a5a7bec103..1d646a86ebb3b 100644
--- a/packages/next-swc/package.json
+++ b/packages/next-swc/package.json
@@ -16,6 +16,7 @@
     "build-native-wasi": "npx --package=@napi-rs/cli@3.0.0-alpha.45 napi build --platform --target wasm32-wasip1-threads -p next-napi-bindings --cwd ../../ --output-dir packages/next-swc/native --no-default-features",
     "build-wasm": "wasm-pack build ../../crates/wasm --scope=next",
     "cache-build-native": "[ -d native ] && echo $(ls native)",
+    "rust-fingerprint": "node ../../scripts/rust-fingerprint.js",
     "rust-check-clippy": "cargo clippy --workspace --all-targets -- -D warnings -A deprecated",
     "rust-check-doc": "RUSTDOCFLAGS='-Zunstable-options --output-format=json' cargo doc --no-deps --workspace",
     "rust-check-fmt": "cd ../..; cargo fmt -- --check",
diff --git a/packages/next-swc/turbo.jsonc b/packages/next-swc/turbo.jsonc
index 36fced8ad2368..0c8f9de1e90a6 100644
--- a/packages/next-swc/turbo.jsonc
+++ b/packages/next-swc/turbo.jsonc
@@ -2,21 +2,28 @@
   "$schema": "https://turborepo.org/schema.json",
   "extends": ["//"],
   "tasks": {
-    // "auto" is used by the workspace `pnpm build-all` script. It checks to see
-    // if there's already an up-to-date precompiled version of turbopack
-    // available before performing the build.
-    "build-native-auto": {
+    // Fingerprint all Rust inputs into a single stamp file. Every Rust task
+    // depends on this, so they only need inputs: [stamp file] instead of
+    // repeating the full list of Rust source globs.
+    "rust-fingerprint": {
       "inputs": [
         "../../.cargo/**",
         "../../crates/**",
         "../../turbopack/crates/**",
+        "!../../crates/*/tests/**",
         "!../../turbopack/crates/*/tests/**",
-        "../../Cargo.toml",
+        "../../**/Cargo.toml",
         "../../Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
         "../../rust-toolchain.toml",
       ],
-      "env": ["CI"],
+      "outputs": ["../../target/.rust-fingerprint"],
+      "cache": false,
+    },
+
+    // "auto" is used by the workspace `pnpm build-all` script.
+    "build-native-auto": {
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
       "outputs": [
         "native/*.node",
         "native/index.d.ts",
@@ -24,115 +31,43 @@
       ],
     },
     "build-native": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "!../../turbopack/crates/*/tests/**",
-        "../../Cargo.toml",
-        "../../Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
-      "env": ["CI"],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
       "outputs": ["native/*.node", "native/index.d.ts"],
     },
     "build-native-release": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "!../../turbopack/crates/*/tests/**",
-        "../../**/Cargo.toml",
-        "../../**/Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
-      "env": ["CI"],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
       "outputs": ["native/*.node", "native/index.d.ts"],
     },
     "build-native-release-with-assertions": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "!../../turbopack/crates/*/tests/**",
-        "../../**/Cargo.toml",
-        "../../**/Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
-      "env": ["CI"],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
       "outputs": ["native/*.node", "native/index.d.ts"],
     },
     "build-native-no-plugin": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "!../../turbopack/crates/*/tests/**",
-        "../../**/Cargo.toml",
-        "../../**/Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
-      "env": ["CI"],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
       "outputs": ["native/*.node", "native/index.d.ts"],
     },
     "build-native-no-plugin-release": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "!../../turbopack/crates/*/tests/**",
-        "../../**/Cargo.toml",
-        "../../**/Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
-      "env": ["CI"],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
       "outputs": ["native/*.node", "native/index.d.ts"],
     },
     "build-wasm": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "!../../turbopack/crates/*/tests/**",
-        "../../**/Cargo.toml",
-        "../../**/Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
-      "env": ["CI"],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
       "outputs": ["../../crates/wasm/pkg/*"],
     },
     "build-native-wasi": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "!../../turbopack/crates/*/tests/**",
-        "../../**/Cargo.toml",
-        "../../**/Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
-      "env": ["CI"],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
       "outputs": ["native/*"],
     },
     "cache-build-native": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "!../../turbopack/crates/*/tests/**",
-        "../../**/Cargo.toml",
-        "../../**/Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
-      "env": ["CI"],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
       "outputs": ["native/*.node", "native/index.d.ts"],
     },
     "rust-check": {
@@ -144,60 +79,25 @@
       ],
     },
     "rust-check-clippy": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "../../**/Cargo.toml",
-        "../../**/Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
     },
     "rust-check-doc": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "../../**/Cargo.toml",
-        "../../**/Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
     },
     "rust-check-fmt": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "../../**/Cargo.toml",
-        "../../**/Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
       "cache": false,
     },
     "rust-check-napi": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "../../**/Cargo.toml",
-        "../../**/Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
     },
     "test-cargo-unit": {
-      "inputs": [
-        "../../.cargo/**",
-        "../../crates/**",
-        "../../turbopack/crates/**",
-        "../../**/Cargo.toml",
-        "../../**/Cargo.lock",
-        "../../.github/workflows/build_and_deploy.yml",
-        "../../rust-toolchain.toml",
-      ],
+      "dependsOn": ["rust-fingerprint"],
+      "inputs": ["../../target/.rust-fingerprint"],
     },
   },
 }
diff --git a/scripts/rust-fingerprint.js b/scripts/rust-fingerprint.js
new file mode 100644
index 0000000000000..d3efc50c09ac3
--- /dev/null
+++ b/scripts/rust-fingerprint.js
@@ -0,0 +1,19 @@
+#!/usr/bin/env node
+// Write the turbo-computed TURBO_HASH to a stamp file.
+// This is used as a turbo task whose only purpose is to compute
+// a fingerprint of all Rust inputs. Other scripts (native-cache.js)
+// read this stamp to get a cache key without re-hashing everything.
+
+const fs = require('fs')
+const path = require('path')
+
+const stamp = path.resolve(__dirname, '..', 'target', '.rust-fingerprint')
+
+if (!process.env.TURBO_HASH) {
+  console.log('rust-fingerprint: skipping (not running under turbo)')
+  process.exit(0)
+}
+
+fs.mkdirSync(path.dirname(stamp), { recursive: true })
+fs.writeFileSync(stamp, process.env.TURBO_HASH)
+console.log(`rust-fingerprint: ${process.env.TURBO_HASH}`)
diff --git a/turbo.json b/turbo.json
index 64b27c2664525..9fd907491b6bf 100644
--- a/turbo.json
+++ b/turbo.json
@@ -1,6 +1,7 @@
 {
   "$schema": "https://turborepo.org/schema.json",
-  "globalEnv": ["NEXT_CI_RUNNER"],
+  "globalEnv": ["CI", "NEXT_CI_RUNNER"],
+  "globalPassThroughEnv": ["RUSTC_WRAPPER", "SCCACHE_*"],
   "tasks": {
     "build": {
       "dependsOn": ["^build"],

PATCH

echo "Patch applied successfully."

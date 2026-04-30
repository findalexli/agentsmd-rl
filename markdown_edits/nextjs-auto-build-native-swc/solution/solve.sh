#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if [ -f packages/next-swc/maybe-build-native.mjs ]; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index 87864950b1315c..d00760084ff7a1 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -367,8 +367,7 @@ When running Next.js integration tests, you must rebuild if source files have ch

 - **First run after branch switch/bootstrap (or if unsure)?** → `pnpm build`
 - **Edited only core Next.js files (`packages/next/**`) after bootstrap?** → `pnpm --filter=next build`
-- **Edited Turbopack (Rust)?** → `pnpm swc-build-native`
-- **Edited both?** → `pnpm turbo build build-native`
+- **Edited Next.js code or Turbopack (Rust)?** → `pnpm build`

 ## Development Anti-Patterns

diff --git a/packages/next-swc/maybe-build-native.mjs b/packages/next-swc/maybe-build-native.mjs
new file mode 100644
index 00000000000000..71dcd01c1e48cc
--- /dev/null
+++ b/packages/next-swc/maybe-build-native.mjs
@@ -0,0 +1,110 @@
+import { execSync } from 'child_process'
+import { readdirSync, rmSync } from 'fs'
+import { dirname, join } from 'path'
+import { fileURLToPath } from 'url'
+
+const __dirname = dirname(fileURLToPath(import.meta.url))
+const PKG_DIR = __dirname
+const ROOT_DIR = join(__dirname, '../..')
+const NATIVE_DIR = join(PKG_DIR, 'native')
+
+function hasExistingNativeBinary() {
+  try {
+    const files = readdirSync(NATIVE_DIR)
+    return files.some((f) => f.endsWith('.node'))
+  } catch {
+    return false
+  }
+}
+
+function clearNativeBinaries() {
+  try {
+    const files = readdirSync(NATIVE_DIR)
+    for (const f of files) {
+      if (f.endsWith('.node')) {
+        rmSync(join(NATIVE_DIR, f))
+      }
+    }
+  } catch {
+    // directory doesn't exist, nothing to clear
+  }
+}
+
+function getVersionBumpCommit() {
+  try {
+    return (
+      execSync(
+        `git log -1 --format=%H -G '"version":' -- packages/next/package.json`,
+        { cwd: ROOT_DIR, encoding: 'utf8' }
+      ).trim() || null
+    )
+  } catch {
+    return null
+  }
+}
+
+function hasRustChanges(sinceCommit) {
+  try {
+    // Omit HEAD to compare against the working tree, which includes
+    // committed, staged, and unstaged changes.
+    const diff = execSync(
+      `git diff --name-only ${sinceCommit} -- ':(glob)**/*.rs' ':(glob)**/*.toml' ':(glob).cargo/**' Cargo.lock rust-toolchain`,
+      { cwd: ROOT_DIR, encoding: 'utf8' }
+    ).trim()
+    return diff.length > 0
+  } catch {
+    // If we can't determine whether changes occurred, assume they did
+    return true
+  }
+}
+
+function buildNative() {
+  console.log('Running swc-build-native...')
+  execSync('pnpm run swc-build-native', {
+    cwd: ROOT_DIR,
+    stdio: 'inherit',
+    env: {
+      ...process.env,
+      CARGO_TERM_COLOR: 'always',
+      TTY: '1',
+    },
+  })
+}
+
+function main() {
+  if (process.env.CI) {
+    console.log('Skipping swc-build-native in CI')
+    return
+  }
+
+  const versionBumpCommit = getVersionBumpCommit()
+
+  if (!versionBumpCommit) {
+    console.log(
+      'Could not determine version bump commit (shallow clone?), building native to be safe...'
+    )
+    buildNative()
+    return
+  }
+
+  if (hasRustChanges(versionBumpCommit)) {
+    console.log(
+      'Rust source files changed since last version bump, building native...'
+    )
+    buildNative()
+    return
+  }
+
+  // No Rust changes from the release version — clear any stale native build
+  // so the prebuilt @next/swc-* npm packages are used instead.
+  if (hasExistingNativeBinary()) {
+    console.log(
+      'No Rust changes since last version bump, clearing stale native binary...'
+    )
+    clearNativeBinaries()
+  }
+
+  console.log('Skipping swc-build-native (no Rust changes since version bump)')
+}
+
+main()
diff --git a/packages/next-swc/package.json b/packages/next-swc/package.json
index dfa235bdc1d279..068809586be081 100644
--- a/packages/next-swc/package.json
+++ b/packages/next-swc/package.json
@@ -6,6 +6,7 @@
     "native/"
   ],
   "scripts": {
+    "build": "node maybe-build-native.mjs",
     "clean": "node ../../scripts/rm.mjs native",
     "build-native": "napi build --platform -p next-napi-bindings --cargo-cwd ../../ --cargo-name next_napi_bindings --features plugin,image-extended --js false native",
     "build-native-release": "napi build --platform -p next-napi-bindings --cargo-cwd ../../ --cargo-name next_napi_bindings --release --features plugin,image-extended,tracing/release_max_level_trace --js false native",
diff --git a/packages/next-swc/turbo.json b/packages/next-swc/turbo.json
index dde214ce4d7667..cdf18b5c8335dc 100644
--- a/packages/next-swc/turbo.json
+++ b/packages/next-swc/turbo.json
@@ -2,6 +2,23 @@
   "$schema": "https://turborepo.org/schema.json",
   "extends": ["//"],
   "tasks": {
+    "build": {
+      "inputs": [
+        "../../.cargo/**",
+        "../../crates/**",
+        "../../turbopack/crates/**",
+        "../../Cargo.toml",
+        "../../Cargo.lock",
+        "../../.github/workflows/build_and_deploy.yml",
+        "../../rust-toolchain"
+      ],
+      "env": ["CI"],
+      "outputs": [
+        "native/*.node",
+        "native/index.d.ts",
+        "../../packages/next/src/build/swc/generated-native.d.ts"
+      ]
+    },
     "build-native": {
       "inputs": [
         "../../.cargo/**",
@@ -13,7 +30,7 @@
         "../../rust-toolchain"
       ],
       "env": ["CI"],
-      "outputs": ["native/*.node"]
+      "outputs": ["native/*.node", "native/index.d.ts"]
     },
     "build-native-release": {
       "inputs": [
@@ -26,7 +43,7 @@
         "../../rust-toolchain"
       ],
       "env": ["CI"],
-      "outputs": ["native/*.node"]
+      "outputs": ["native/*.node", "native/index.d.ts"]
     },
     "build-native-release-with-assertions": {
       "inputs": [
@@ -39,7 +56,7 @@
         "../../rust-toolchain"
       ],
       "env": ["CI"],
-      "outputs": ["native/*.node"]
+      "outputs": ["native/*.node", "native/index.d.ts"]
     },
     "build-native-no-plugin": {
       "inputs": [
@@ -52,7 +69,7 @@
         "../../rust-toolchain"
       ],
       "env": ["CI"],
-      "outputs": ["native/*.node"]
+      "outputs": ["native/*.node", "native/index.d.ts"]
     },
     "build-native-no-plugin-release": {
       "inputs": [
@@ -65,7 +82,7 @@
         "../../rust-toolchain"
       ],
       "env": ["CI"],
-      "outputs": ["native/*.node"]
+      "outputs": ["native/*.node", "native/index.d.ts"]
     },
     "build-wasm": {
       "inputs": [
@@ -104,7 +121,7 @@
         "../../rust-toolchain"
       ],
       "env": ["CI"],
-      "outputs": ["native/*.node"]
+      "outputs": ["native/*.node", "native/index.d.ts"]
     },
     "rust-check": {
       "dependsOn": ["rust-check-fmt", "rust-check-clippy", "rust-check-napi"]
diff --git a/scripts/build-native.ts b/scripts/build-native.ts
index 6f3b757b6126ef..734b01fc807987 100644
--- a/scripts/build-native.ts
+++ b/scripts/build-native.ts
@@ -4,7 +4,7 @@ import { promises as fs } from 'node:fs'
 import path from 'node:path'
 import url from 'node:url'
 import execa from 'execa'
-import { NEXT_DIR, logCommand, execFn } from './pack-util'
+import { NEXT_DIR, logCommand } from './pack-util'

 const nextSwcDir = path.join(NEXT_DIR, 'packages/next-swc')

@@ -25,10 +25,7 @@ export default async function buildNative(
     stdio: 'inherit',
   })

-  await execFn(
-    'Copy generated types to `next/src/build/swc/generated-native.d.ts`',
-    () => writeTypes()
-  )
+  await writeTypes()
 }

 // Check if this file is being run directly
@@ -56,17 +53,31 @@ async function writeTypes() {
   const generatedTypes = await fs.readFile(generatedTypesPath, 'utf8')
   let vendoredTypes = await fs.readFile(vendoredTypesPath, 'utf8')

+  const existingContent = vendoredTypes
   vendoredTypes = vendoredTypes.split(generatedTypesMarker)[0]
   vendoredTypes =
     vendoredTypes + generatedTypesMarker + generatedNotice + generatedTypes

-  await fs.writeFile(vendoredTypesPath, vendoredTypes)
-
-  const prettifyCommand = ['prettier', '--write', vendoredTypesPath]
+  const prettifyCommand = ['prettier', '--stdin-filepath', vendoredTypesPath]
   logCommand('Prettify generated types', prettifyCommand)
-  await execa(prettifyCommand[0], prettifyCommand.slice(1), {
-    cwd: NEXT_DIR,
-    stdio: 'inherit',
-    preferLocal: true,
-  })
+  const prettierResult = await execa(
+    prettifyCommand[0],
+    prettifyCommand.slice(1),
+    {
+      cwd: NEXT_DIR,
+      input: vendoredTypes,
+      preferLocal: true,
+    }
+  )
+  vendoredTypes = prettierResult.stdout
+  if (!vendoredTypes.endsWith('\n')) {
+    vendoredTypes += '\n'
+  }
+
+  if (vendoredTypes === existingContent) {
+    return
+  }
+
+  logCommand('Write generated types', `write file`)
+  await fs.writeFile(vendoredTypesPath, vendoredTypes)
 }

PATCH

echo "Patch applied successfully."

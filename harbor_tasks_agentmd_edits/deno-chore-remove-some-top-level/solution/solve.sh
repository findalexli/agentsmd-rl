#!/usr/bin/env bash
set -euo pipefail

cd /workspace/deno

# Idempotent: skip if already applied
if [ -d "tests/bench_util" ] && [ ! -d "bench_util" ]; then
    echo "Patch already applied."
    exit 0
fi

# Apply patch
git apply - <<'PATCH'
diff --git a/Cargo.toml b/Cargo.toml
index bf5dae979a6f44..51b40a75f5e343 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -3,7 +3,6 @@
 [workspace]
 resolver = "2"
 members = [
-  "bench_util",
   "cli",
   "cli/lib",
   "cli/rt",
@@ -48,6 +47,7 @@ members = [
   "runtime/permissions",
   "runtime/subprocess_windows",
   "tests",
+  "tests/bench_util",
   "tests/ffi",
   "tests/napi",
   "tests/sqlite_extension_test",
@@ -118,7 +118,7 @@ deno_webstorage = { version = "0.225.0", path = "./ext/webstorage" }
 denort_helper = { version = "0.28.0", path = "./ext/rt_helper" }

 # workspace libraries
-deno_bench_util = { version = "0.224.0", path = "./bench_util" }
+deno_bench_util = { version = "0.224.0", path = "./tests/bench_util" }
 deno_config = { version = "0.80.0", features = ["workspace"], path = "./libs/config" }
 deno_crypto_provider = { version = "0.24.0", path = "./libs/crypto" }
 deno_features = { version = "0.27.0", path = "./runtime/features" }
diff --git a/cli/tsc/README.md b/cli/tsc/README.md
index 4c021199f58c0c..a59ea732cbe54e 100644
--- a/cli/tsc/README.md
+++ b/cli/tsc/README.md
@@ -33,3 +33,42 @@ npx hereby
 rsync built/local/typescript.js ~/src/deno/cli/tsc/00_typescript.js
 rsync --exclude=protocol.d.ts --exclude=tsserverlibrary.d.ts --exclude=typescriptServices.d.ts built/local/*.d.ts ~/src/deno/cli/tsc/dts/
 ```
+
+## Typescript-Go Integration
+
+Currently only integrated with deno check, though in the future it will also be
+integrated with our LSP implementation.
+
+In the CLI, we have a small abstraction over the tsc backend in
+[cli/tsc/mod.rs](./mod.rs). Along with some shared types and functionality, the
+main piece is the `exec` function, which takes a "request" to be served by the
+typescript compiler and returns the result. This now has two different "backend"
+which can serve the request – the current tsc, which runs in an isolate and
+communicates via ops, and typescript-go which runs in a subprocess and uses IPC.
+
+From a high level, the way the tsgo backend works is that we download a
+typescript-go binary from
+[github releases](https://github.com/denoland/typescript-go/releases) into the
+deno cache dir. To actually interface with tsgo, we spawn it in a subprocess and
+write messages over stdin/stdout (similar to the Language Server Protocol). The
+format is a mixture of binary data (for the header and other protocol level
+details) followed by json encoded values for RPC calls. The rust implementation
+of the IPC protocol is in the
+[deno_typescript_go_client_rust crate](../libs/typescript_go_client/src/lib.rs).
+
+We currently maintain a
+[fork of typescript-go](https://github.com/denoland/typescript-go) with the
+following changes:
+
+- Special handling of the global symbol tables to account for the fact that we
+  have two slightly different sets of globals: one for node contexts (in npm
+  packages), and one for deno contexts. At this point, the main difference is
+  the type returned by `setTimeout`. With node globals `setTimeout` returns an
+  object, and with deno globals it returns a number (just like the web
+  standard).
+- Symbol table logic to prevent @types/node from creating type errors by
+  introducing incompatible definitions for globals
+- Additional hooks to allow us to provide our own resolution, determine whether
+  a file is esm/cjs, etc.
+- Additional APIs exposed from the IPC server
+- Support for deno's custom libs (`deno.window`, `deno.worker`, etc)
diff --git a/docs/tsgo.md b/docs/tsgo.md
deleted file mode 100644
index c1e081a69952e6..00000000000000
--- a/docs/tsgo.md
+++ /dev/null
@@ -1,39 +0,0 @@
-# Typescript-Go Integration
-
-Currently only integrated with deno check, though in the future it will also be
-integrated with our LSP implementation.
-
-In the CLI, we have a small abstraction over the tsc backend in
-[cli/tsc/mod.rs](../cli/tsc/mod.rs). Along with some shared types and
-functionality, the main piece is the `exec` function, which takes a "request" to
-be served by the typescript compiler and returns the result. This now has two
diff --git a/tools/lint.js b/tools/lint.js
index 8813c9594aaa0f..a7f3637cb9033c 100755
--- a/tools/lint.js
+++ b/tools/lint.js
@@ -38,7 +38,7 @@ if (js) {
   promises.push(dlintPreferPrimordials());
   promises.push(ensureCiYmlUpToDate());
   promises.push(ensureNoUnusedOutFiles());
-  promises.push(ensureNoNewTopLevelFiles());
+  promises.push(ensureNoNewTopLevelEntries());

   if (rs) {
     promises.push(checkCopyright());
@@ -325,29 +325,42 @@ async function ensureNoUnusedOutFiles() {
   }
 }

-async function listTopLevelFiles() {
+async function listTopLevelEntries() {
   const files = await gitLsFiles(ROOT_PATH, []);
+  const rootPrefix = ROOT_PATH.replace(new RegExp(SEPARATOR + "$"), "") +
+    SEPARATOR;
   return [
     ...new Set(
-      files.map((f) =>
-        f.replace(
-          ROOT_PATH.replace(new RegExp(SEPARATOR + "$"), "") + SEPARATOR,
-          "",
-        )
-      )
-        .filter((file) => !file.includes(SEPARATOR)),
+      files.map((f) => f.replace(rootPrefix, ""))
+        .map((file) => {
+          const sepIndex = file.indexOf(SEPARATOR);
+          // top-level file or first path component (directory)
+          return sepIndex === -1 ? file : file.substring(0, sepIndex);
+        }),
     ),
   ].sort();
 }

-async function ensureNoNewTopLevelFiles() {
-  const currentFiles = await listTopLevelFiles();
-
-  const allowedFiles = [
+async function ensureNoNewTopLevelEntries() {
+  const currentEntries = await listTopLevelEntries();
+
+  // WARNING: When adding anything to this list it must be discussed!
+  // Keep the root of the repository clean.
+  const allowed = new Set([
+    ".cargo",
+    ".devcontainer",
+    ".github",
+    "cli",
+    "ext",
+    "libs",
+    "runtime",
+    "tests",
+    "tools",
     ".dlint.json",
     ".dprint.json",
     ".editorconfig",
     ".gitattributes",
+    // WARNING! See Notice above before adding anything here
     ".gitignore",
     ".gitmodules",
     ".rustfmt.toml",
@@ -361,14 +374,14 @@ async function ensureNoNewTopLevelFiles() {
     "rust-toolchain.toml",
     "flake.nix",
     "flake.lock",
-  ].sort();
+  ]);

-  const newFiles = currentFiles.filter((file) => !allowedFiles.includes(file));
-  if (newFiles.length > 0) {
+  const newEntries = currentEntries.filter((e) => !allowed.has(e));
+  if (newEntries.length > 0) {
     throw new Error(
-      `New top-level files detected: ${newFiles.join(", ")}. ` +
-        `Only the following top-level files are allowed: ${
-          allowedFiles.join(", ")
+      `New top-level entries detected: ${newEntries.join(", ")}. ` +
+        `Only the following top-level entries are allowed: ${
+          allowed.join(", ")
         }`,
     );
   }
PATCH

# Move bench_util directory manually (git apply handles the content changes but not the rename)
if [ -d "bench_util" ] && [ ! -d "tests/bench_util" ]; then
    mkdir -p tests/bench_util
    cp -r bench_util/* tests/bench_util/
    rm -rf bench_util
fi

# Remove docs/tsgo.md if it exists
if [ -f "docs/tsgo.md" ]; then
    rm docs/tsgo.md
fi

echo "Patch applied successfully."

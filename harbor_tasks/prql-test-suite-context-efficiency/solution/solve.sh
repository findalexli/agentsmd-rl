#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prql

# Idempotency guard — distinctive line from the patch
if grep -q '^      NEXTEST_STATUS_LEVEL: fail$' Taskfile.yaml 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index e20efc94f18b..98173334e7a8 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -1,42 +1,51 @@
 # Claude

-## Tests
+## Development Workflow

-Prefer `cargo insta` tests.
+Use a tight inner loop for fast feedback, comprehensive outer loop before
+returning to user:

-When running tests, prefer:
+**Inner loop** (fast, focused, <5s):

 ```sh
-# Run tests and automatically accept snapshot changes
-cargo insta test --accept
-
-# Run tests in a specific package
-cargo insta test -p prqlc-parser --accept
+# Run lints on changed files
+task test-lint

-# Run tests matching a specific pattern
+# Run specific tests you're working on
 cargo insta test -p prqlc --test integration -- date
+
+# Run unit tests for a specific module
+cargo insta test -p prqlc --lib semantic::resolver
+```
+
+**Outer loop** (comprehensive, ~1min, before returning to user):
+
+```sh
+# Run everything - this is required before returning
+task test-all
 ```

+The test suite is configured to minimize token usage:
+
+- **Nextest** only shows failures and slow tests (not 600 PASS lines)
+- **Cargo builds** use `--quiet` flag (no compilation spam)
+- **Result**: ~52% reduction in output (1128 → 540 lines, ~4.5k tokens)
+
+## Tests
+
 Prefer inline snapshots for almost all tests:

 ```rust
 insta::assert_snapshot!(result, @"expected output");
 ```

-Initializing the test with:
+Initialize tests with empty snapshots, then run with `--accept`:

 ```rust
 insta::assert_snapshot!(result, @"");
 ```

-...and then running the test commands above with `--accept` will then fill in
-the result.
-
-To run all tests, accepting snapshots, run
-
-```sh
-task test-all
-```
+The test commands above with `--accept` will fill in the result automatically.

 ## Running the CLI

diff --git a/Taskfile.yaml b/Taskfile.yaml
index ae636047b89e..7148a5a820d2 100644
--- a/Taskfile.yaml
+++ b/Taskfile.yaml
@@ -230,14 +230,15 @@ tasks:

       Running this isn't required when developing; it's for caching or as a reference.
     cmds:
-      - cargo build --all-targets --all-features
+      - cargo build --all-targets --all-features --quiet
       - cargo build --all-targets --all-features --target=wasm32-unknown-unknown
+        --quiet
       # Build without features, as the dependencies have slightly different
       # features themselves and so require recompiling. This is only useful for
       # caching.
-      - cargo build --all-targets
-      - cargo build --all-targets --features=default,test-dbs
-      - cargo doc
+      - cargo build --all-targets --quiet
+      - cargo build --all-targets --features=default,test-dbs --quiet
+      - cargo doc --quiet
       - task: build-each-crate
       - task: web:build
       - task: python:build
@@ -258,7 +259,7 @@ tasks:
     cmds:
       - |
         {{ range ( .PACKAGES | splitLines ) -}}
-        cargo build --all-targets -p {{ . }}
+        cargo build --all-targets -p {{ . }} --quiet
         {{ end -}}

   test-rust-api:
@@ -305,6 +306,10 @@ tasks:
     #   - "**/*.toml"
     #   - "**/*.lock"
     #   - "**/*.snap"
+    env:
+      NEXTEST_STATUS_LEVEL: fail
+      NEXTEST_FINAL_STATUS_LEVEL: slow
+      NEXTEST_HIDE_PROGRESS_BAR: "true"
     cmds:
       - cargo insta test --accept --features=default,test-dbs
         --test-runner=nextest --unreferenced=auto
PATCH

echo "Gold patch applied"

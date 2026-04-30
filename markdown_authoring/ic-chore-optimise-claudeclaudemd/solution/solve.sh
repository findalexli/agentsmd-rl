#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ic

# Idempotency guard
if grep -qF "After changing Rust code (`*.rs`) first format the code using:" ".claude/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -1,7 +1,11 @@
 Rust
 ====
 
-After changing Rust code (`*.rs`) first format the code using `cargo fmt`.
+After changing Rust code (`*.rs`) first format the code using:
+
+```
+cargo fmt -- <MODIFIED_RUST_FILES>
+````
 
 Then check the code for linting errors using:
 
@@ -43,5 +47,3 @@ Testing
 After code can be built it needs to be tested.
 
 After changing a package under `rs/$PACKAGE` run `bazel test //rs/$PACKAGE`.
-
-Tests under `rs/tests` which are defined using the `system_test` bazel macro are end-to-end tests which are called system-tests. These tests are comprehensive but also slow and harder to debug. So run them last or wait for GitHub Actions to run them on your Pull Request.
\ No newline at end of file
PATCH

echo "Gold patch applied."

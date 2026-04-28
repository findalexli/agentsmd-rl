#!/usr/bin/env bash
set -euo pipefail

cd /workspace/redb

# Idempotency guard
if grep -qF "Changes that are significant to users should be documented in `CHANGELOG.md`. En" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -31,6 +31,11 @@ fix the underlying issue — do not bypass checks.
 If you are touching workspace crates beyond the main `redb` crate, run
 `just test_all` instead, which also builds and tests the full workspace.
 
+## Release notes
+
+Changes that are significant to users should be documented in `CHANGELOG.md`. Entries should be
+brief and focus on the user-facing impact of the change, not on implementation details.
+
 ## Fuzzing
 
 `just fuzz` runs the libFuzzer-based harness under `fuzz/` (`fuzz_redb`) with
PATCH

echo "Gold patch applied."

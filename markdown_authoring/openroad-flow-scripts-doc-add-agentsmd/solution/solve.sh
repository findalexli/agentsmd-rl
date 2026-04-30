#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openroad-flow-scripts

# Idempotency guard
if grep -qF "The OpenROAD (OR) engine source resides in `tools/OpenROAD/` (git submodule). Fo" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,5 @@
+# OpenROAD-flow-scripts (ORFS) agent context
+
+See `README.md` for the general ORFS guide.
+
+The OpenROAD (OR) engine source resides in `tools/OpenROAD/` (git submodule). For C++/Tcl development, refer to `tools/OpenROAD/AGENTS.md`.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."

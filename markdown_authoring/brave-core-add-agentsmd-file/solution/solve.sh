#!/usr/bin/env bash
set -euo pipefail

cd /workspace/brave-core

# Idempotency guard
if grep -qF "Refer to canonical agent instructions in `.claude/CLAUDE.md`." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1 @@
+Refer to canonical agent instructions in `.claude/CLAUDE.md`.
PATCH

echo "Gold patch applied."

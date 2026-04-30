#!/usr/bin/env bash
set -euo pipefail

cd /workspace/chart-visualization-skills

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md" && grep -qF "See [AGENTS.md](./AGENTS.md) for project architecture and structure." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md

diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1 +1 @@
-See [Agent.md](./Agent.md) for project architecture and structure.
+See [AGENTS.md](./AGENTS.md) for project architecture and structure.
PATCH

echo "Gold patch applied."

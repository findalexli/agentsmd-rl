#!/usr/bin/env bash
set -euo pipefail

cd /workspace/yfinance-mcp

# Idempotency guard
if grep -qF "Read [AGENTS.md](../AGENTS.md) and [CLAUDE.md](../CLAUDE.md) files for for instr" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1 +1 @@
-Read [AGENTS.md](./AGENTS.md) and [CLAUDE.md](./CLAUDE.md) files for for instructions.
+Read [AGENTS.md](../AGENTS.md) and [CLAUDE.md](../CLAUDE.md) files for for instructions.
PATCH

echo "Gold patch applied."

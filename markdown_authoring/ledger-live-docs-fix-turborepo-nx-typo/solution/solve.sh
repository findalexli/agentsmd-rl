#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ledger-live

# Idempotency guard
if grep -qF "- This pnpm and nx monorepo provides frontend apps" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -3,7 +3,7 @@
 ## Overview
 
 - "Ledger Wallet" (formerly "ledger-live") is a crypto wallet
-- This pnpm and turborepo monorepo provides frontend apps
+- This pnpm and nx monorepo provides frontend apps
 
 ## Common Commands
 
PATCH

echo "Gold patch applied."

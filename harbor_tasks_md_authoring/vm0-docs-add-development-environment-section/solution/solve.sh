#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vm0

# Idempotency guard
if grep -qF "- **main branch is always stable** - All code merged to main has passed CI (buil" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,5 +1,16 @@
 # Claude Code Project Guidelines
 
+## Development Environment
+
+**Claude Code runs in an isolated Docker container** with its own PostgreSQL server. This environment is completely separate from production.
+
+### Key Assumptions
+
+- **main branch is always stable** - All code merged to main has passed CI (build + tests). If your branch fails to build or pass tests, the issue is in your branch code, not main.
+- **Use dev-tunnel for local development** - Run `/dev-tunnel` to start a local server accessible by sandbox webhooks. Without this, webhooks cannot reach your local server.
+- **Run `pnpm db:migrate` to sync database** - After pulling new changes, run this command in the `turbo` directory to apply the latest migrations.
+- **Run `script/sync-env.sh` to sync environment variables** - If missing required environment variables, ask the user to run this script to sync `.env.local`.
+
 ## Global Services Pattern
 
 ### How to Use Services
PATCH

echo "Gold patch applied."

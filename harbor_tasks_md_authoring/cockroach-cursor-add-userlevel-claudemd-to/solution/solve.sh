#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cockroach

# Idempotency guard
if grep -qF "- Enforce [`CLAUDE.local.md`](../../CLAUDE.local.md), `$HOME/CLAUDE.md`, and [`C" ".cursor/rules/main.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/main.mdc b/.cursor/rules/main.mdc
@@ -6,6 +6,5 @@ globs:
 alwaysApply: true
 ---
 
-- **ALWAYS** read and cache [`CLAUDE.md`](../../CLAUDE.md) (and [`CLAUDE.local.md`](../../CLAUDE.local.md), if present) at conversation start, **without exception**.
-- Enforce [`CLAUDE.md`](../../CLAUDE.md) for all messages in the session.
-- Enforce [`CLAUDE.local.md`](../../CLAUDE.local.md) additively; on conflict, prefer [`CLAUDE.md`](../../CLAUDE.md).
+- **ALWAYS** read and cache [`CLAUDE.md`](../../CLAUDE.md) at conversation start, **without exception**. If present, **always** read and cache `$HOME/CLAUDE.md` and [`CLAUDE.local.md`](../../CLAUDE.local.md), also **without exception**.
+- Enforce [`CLAUDE.local.md`](../../CLAUDE.local.md), `$HOME/CLAUDE.md`, and [`CLAUDE.md`](../../CLAUDE.md) for all messages in the session. On conflict, prefer [`CLAUDE.local.md`](../../CLAUDE.local.md), then `$HOME/CLAUDE.md`, then [`CLAUDE.md`](../../CLAUDE.md).
PATCH

echo "Gold patch applied."

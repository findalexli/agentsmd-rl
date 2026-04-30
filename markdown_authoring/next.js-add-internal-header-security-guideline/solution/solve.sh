#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency guard
if grep -qF "**When reviewing PRs: if new code reads a request header that is not a standard " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -430,3 +430,9 @@ If Turbopack produces unexpected errors after switching branches or pulling, che
 - Account for empty lines, import statements, and type imports that shift line numbers
 - Highlights should point to the actual relevant code, not unrelated lines like `return (` or framework boilerplate
 - Double-check highlights by counting lines from 1 within each code block
+
+### Server Security: Internal Header Filtering
+
+Next.js strips internal headers from incoming requests via `filterInternalHeaders()` in `packages/next/src/server/lib/server-ipc/utils.ts`. This runs at the entry point in `packages/next/src/server/lib/router-server.ts` before any server code executes. Only headers listed in the `INTERNAL_HEADERS` array are stripped.
+
+**When reviewing PRs: if new code reads a request header that is not a standard HTTP header (like `content-type`, `accept`, `user-agent`, `host`, `authorization`, `cookie`, etc.), flag it for security review.** The header may be forgeable by an external attacker if it is not in the `INTERNAL_HEADERS` filter list in `packages/next/src/server/lib/server-ipc/utils.ts`.
PATCH

echo "Gold patch applied."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- Add `refetchInterval: 30_000` to list, count, and detail query factories that " "ui-v2/src/api/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui-v2/src/api/AGENTS.md b/ui-v2/src/api/AGENTS.md
@@ -27,6 +27,7 @@ This directory contains API-related code including query options factories and m
 - For queries where errors are expected and should not be retried (e.g., existence checks where 404 means "name is available"), set `retry: false` in the `queryOptions`.
 - When mutating, create custom hooks for each mutation
 - Don't perform data transformation in queryOptions factories - do it in components
+- Add `refetchInterval: 30_000` to list, count, and detail query factories that display live operational data (work pools, flow runs, task runs, etc.). Use `60_000` for slower-changing data (events). When callers may need to override the interval, accept it as a parameter with a sensible default rather than hardcoding it.
 
 ## Query Key Factory Pattern
 
PATCH

echo "Gold patch applied."

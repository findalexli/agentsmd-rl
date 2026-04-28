#!/usr/bin/env bash
set -euo pipefail

cd /workspace/python-sdk

# Idempotency guard
if grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -48,8 +48,6 @@ This document contains critical information about working with this codebase. Fo
   the problem it tries to solve, and how it is solved. Don't go into the specifics of the
   code unless it adds clarity.
 
-- Always add `jerome3o-anthropic` and `jspahrsummers` as reviewer.
-
 - NEVER ever mention a `co-authored-by` or similar aspects. In particular, never
   mention the tool used to create the commit message or PR.
 
PATCH

echo "Gold patch applied."

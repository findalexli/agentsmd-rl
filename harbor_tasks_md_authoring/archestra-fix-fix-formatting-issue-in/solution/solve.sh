#!/usr/bin/env bash
set -euo pipefail

cd /workspace/archestra

# Idempotency guard
if grep -qF "This file provides guidance to Claude Code (claude.ai/code) when working with co" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,6 +1,6 @@
 # CLAUDE.md
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository
 
 ## Working Directory
 
PATCH

echo "Gold patch applied."

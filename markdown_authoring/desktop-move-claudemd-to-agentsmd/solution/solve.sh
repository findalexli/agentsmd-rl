#!/usr/bin/env bash
set -euo pipefail

cd /workspace/desktop

# Idempotency guard
if grep -qF "Module-specific documentation lives in `AGENTS.md` files within each subdirector" "AGENTS.md" && grep -qF "src/app/AGENTS.md" "src/app/AGENTS.md" && grep -qF "src/app/preload/AGENTS.md" "src/app/preload/AGENTS.md" && grep -qF "src/app/views/AGENTS.md" "src/app/views/AGENTS.md" && grep -qF "src/common/AGENTS.md" "src/common/AGENTS.md" && grep -qF "src/common/config/AGENTS.md" "src/common/config/AGENTS.md" && grep -qF "src/main/AGENTS.md" "src/main/AGENTS.md" && grep -qF "src/main/diagnostics/AGENTS.md" "src/main/diagnostics/AGENTS.md" && grep -qF "src/main/notifications/AGENTS.md" "src/main/notifications/AGENTS.md" && grep -qF "src/main/security/AGENTS.md" "src/main/security/AGENTS.md" && grep -qF "src/renderer/AGENTS.md" "src/renderer/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,4 +1,4 @@
-# CLAUDE.md — Mattermost Desktop App
+# AGENTS.md — Mattermost Desktop App
 
 ## Project overview
 
@@ -55,7 +55,7 @@ src/
 └── types/          # Shared TypeScript type definitions
 ```
 
-Module-specific documentation lives in `CLAUDE.md` files within each subdirectory.
+Module-specific documentation lives in `AGENTS.md` files within each subdirectory.
 
 ## Development
 
diff --git a/src/app/AGENTS.md b/src/app/AGENTS.md

diff --git a/src/app/preload/AGENTS.md b/src/app/preload/AGENTS.md

diff --git a/src/app/views/AGENTS.md b/src/app/views/AGENTS.md

diff --git a/src/common/AGENTS.md b/src/common/AGENTS.md

diff --git a/src/common/config/AGENTS.md b/src/common/config/AGENTS.md

diff --git a/src/main/AGENTS.md b/src/main/AGENTS.md

diff --git a/src/main/diagnostics/AGENTS.md b/src/main/diagnostics/AGENTS.md

diff --git a/src/main/notifications/AGENTS.md b/src/main/notifications/AGENTS.md

diff --git a/src/main/security/AGENTS.md b/src/main/security/AGENTS.md

diff --git a/src/renderer/AGENTS.md b/src/renderer/AGENTS.md

PATCH

echo "Gold patch applied."

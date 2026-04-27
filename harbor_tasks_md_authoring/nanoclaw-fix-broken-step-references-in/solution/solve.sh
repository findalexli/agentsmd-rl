#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "- PLATFORM=macos + APPLE_CONTAINER=installed \u2192 Use `AskUserQuestion: Docker (cro" ".claude/skills/setup/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/setup/SKILL.md b/.claude/skills/setup/SKILL.md
@@ -38,7 +38,7 @@ Run `npx tsx setup/index.ts --step environment` and parse the status block.
 Check the preflight results for `APPLE_CONTAINER` and `DOCKER`, and the PLATFORM from step 1.
 
 - PLATFORM=linux → Docker (only option)
-- PLATFORM=macos + APPLE_CONTAINER=installed → Use `AskUserQuestion: Docker (cross-platform) or Apple Container (native macOS)?` If Apple Container, run `/convert-to-apple-container` now, then skip to 4c.
+- PLATFORM=macos + APPLE_CONTAINER=installed → Use `AskUserQuestion: Docker (cross-platform) or Apple Container (native macOS)?` If Apple Container, run `/convert-to-apple-container` now, then skip to 3c.
 - PLATFORM=macos + APPLE_CONTAINER=not_found → Docker
 
 ### 3a-docker. Install Docker
@@ -59,9 +59,9 @@ grep -q "CONTAINER_RUNTIME_BIN = 'container'" src/container-runtime.ts && echo "
 
 **If NEEDS_CONVERSION**, the source code still uses Docker as the runtime. You MUST run the `/convert-to-apple-container` skill NOW, before proceeding to the build step.
 
-**If ALREADY_CONVERTED**, the code already uses Apple Container. Continue to 4c.
+**If ALREADY_CONVERTED**, the code already uses Apple Container. Continue to 3c.
 
-**If the chosen runtime is Docker**, no conversion is needed. Continue to 4c.
+**If the chosen runtime is Docker**, no conversion is needed. Continue to 3c.
 
 ### 3c. Build and test
 
PATCH

echo "Gold patch applied."

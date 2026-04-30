#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tambo

# Idempotency guard
if grep -qF "**\u26a0\ufe0f IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It" "CLAUDE.md" && grep -qF "**\u26a0\ufe0f IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It" "cli/CLAUDE.md" && grep -qF "**\u26a0\ufe0f IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It" "create-tambo-app/CLAUDE.md" && grep -qF "**\u26a0\ufe0f IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It" "docs/CLAUDE.md" && grep -qF "**\u26a0\ufe0f IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It" "react-sdk/CLAUDE.md" && grep -qF "**\u26a0\ufe0f IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It" "showcase/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -2,7 +2,7 @@
 
 This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
 
-**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and development workflows.**
+**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and development workflows.**
 
 ## Quick Reference
 
@@ -23,4 +23,4 @@ turbo lint              # Lint all packages
 turbo test              # Test all packages
 ```
 
-For detailed information on architecture, development patterns, and cross-package workflows, see [AGENTS.md](./AGENTS.md).
+For detailed information on architecture, development patterns, and cross-package workflows, see @AGENTS.md.
diff --git a/cli/CLAUDE.md b/cli/CLAUDE.md
@@ -2,7 +2,7 @@
 
 This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
 
-**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and command workflows.**
+**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and command workflows.**
 
 ## Quick Reference
 
diff --git a/create-tambo-app/CLAUDE.md b/create-tambo-app/CLAUDE.md
@@ -2,7 +2,7 @@
 
 This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
 
-**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and proxy patterns.**
+**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and proxy patterns.**
 
 ## Quick Reference
 
diff --git a/docs/CLAUDE.md b/docs/CLAUDE.md
@@ -2,7 +2,7 @@
 
 This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
 
-**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and content workflows.**
+**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and content workflows.**
 
 ## Quick Reference
 
diff --git a/react-sdk/CLAUDE.md b/react-sdk/CLAUDE.md
@@ -1,6 +1,6 @@
 # CLAUDE.md
 
-**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and development patterns.**
+**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and development patterns.**
 
 ## Quick Reference
 
diff --git a/showcase/CLAUDE.md b/showcase/CLAUDE.md
@@ -2,7 +2,7 @@
 
 This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
 
-**⚠️ IMPORTANT: Read [AGENTS.md](./AGENTS.md) before making any changes or using any tools. It contains detailed architectural guidance and component patterns.**
+**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and component patterns.**
 
 ## Quick Reference
 
PATCH

echo "Gold patch applied."

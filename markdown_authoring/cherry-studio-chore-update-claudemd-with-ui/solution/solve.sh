#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cherry-studio

# Idempotency guard
if grep -qF "The project is in the process of migrating from antd & styled-components to Hero" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -92,6 +92,12 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 - **Multi-language Support**: i18n with dynamic loading
 - **Theme System**: Light/dark themes with custom CSS variables
 
+### UI Design
+
+The project is in the process of migrating from antd & styled-components to HeroUI. Please use HeroUI to build UI components. The use of antd and styled-components is prohibited.
+
+HeroUI Docs: https://www.heroui.com/docs/guide/introduction
+
 ## Logging Standards
 
 ### Usage
PATCH

echo "Gold patch applied."

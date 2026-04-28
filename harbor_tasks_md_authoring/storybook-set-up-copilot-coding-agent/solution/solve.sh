#!/usr/bin/env bash
set -euo pipefail

cd /workspace/storybook

# Idempotency guard
if grep -qF "- **Package Manager**: Yarn 4.10.3" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -9,7 +9,7 @@ Storybook is a large monorepo built with TypeScript, React, and various other fr
 ## System Requirements
 
 - **Node.js**: 22.21.1 (see `.nvmrc`)
-- **Package Manager**: Yarn 4.9.1
+- **Package Manager**: Yarn 4.10.3
 - **Operating System**: Linux/macOS (CI environment)
 
 ## Repository Structure
PATCH

echo "Gold patch applied."

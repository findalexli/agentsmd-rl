#!/usr/bin/env bash
set -euo pipefail

cd /workspace/efcore

# Idempotency guard
if grep -qF ".github/copilot-instructions.md" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -168,28 +168,6 @@ If you are not sure, do not guess, just tell that you don't know or ask clarifyi
 ## Pull Request Guidelines
 
 - **ALWAYS** target the `main` branch for new PRs unless explicitly instructed otherwise
-- For servicing PRs (fixes targeting release branches), use the following PR description template:
-```
-Fixes #{issue_number}
-
-**Description**
-{Brief description of the issue and fix}
-
-**Customer impact**
-{How does the reported issue affect customers? Are there workarounds?}
-
-**How found**
-{Was it customer reported or found during verification? How many customers are affected?}
-
-**Regression**
-{Is it a regression from a released version? Which one?}
-
-**Testing**
-{How the changes were tested}
-
-**Risk**
-{Low/Medium/High, with justification}
-```
 
 ## Overview of Entity Framework Core
 
PATCH

echo "Gold patch applied."

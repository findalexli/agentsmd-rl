#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ddev

# Idempotency guard
if grep -qF "For standard DDEV organization patterns including communication style, branch na" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,24 +1,8 @@
 # AGENTS.md
 
-This file provides guidance to AI agents when working with code in this repository.
+This file provides guidance to AI agents when working with the DDEV core codebase.
 
-## Communication Style
-
-- Use direct, concise language without unnecessary adjectives or adverbs
-- Avoid flowery or marketing-style language ("tremendous", "dramatically", "revolutionary", "working perfectly", etc.)
-- Don't include flattery or excessive praise ("excellent!", "perfect!", "great job!")
-- State facts and findings directly without embellishment
-- Skip introductory phrases like "I'm excited to", "I'd be happy to", "Let me dive into"
-- Avoid concluding with summary statements unless specifically requested
-- When presenting options or analysis, lead with the core information, not commentary about it
-
-### AI Language Guidelines
-
-- Avoid words that reveal AI writing: "Comprehensive", "works perfectly", "You're absolutely right"
-- Don't say "perfect" in response to actions
-- Don't claim results are "ready for production use" without verification
-
-## Project Overview
+## DDEV Core Project Overview
 
 DDEV is an open-source tool for running local web development environments for PHP and Node.js. It uses Docker containers to provide consistent, isolated development environments with minimal configuration.
 
@@ -375,6 +359,10 @@ For optimal performance with DDEV development, consider these configuration patt
 }
 ```
 
+## General DDEV Development Patterns
+
+For standard DDEV organization patterns including communication style, branch naming, PR creation, and common development practices, see the [organization-wide AGENTS.md](https://github.com/ddev/.github/blob/main/AGENTS.md).
+
 ## Task Master AI Instructions
 
 **Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
PATCH

echo "Gold patch applied."

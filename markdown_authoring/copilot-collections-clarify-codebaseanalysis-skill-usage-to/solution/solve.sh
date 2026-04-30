#!/usr/bin/env bash
set -euo pipefail

cd /workspace/copilot-collections

# Idempotency guard
if grep -qF "- `codebase-analysis` - for the structured codebase analysis process only (note:" ".github/prompts/code-quality-check.prompt.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/prompts/code-quality-check.prompt.md b/.github/prompts/code-quality-check.prompt.md
@@ -9,7 +9,7 @@ Your goal is to perform a thorough code quality analysis of the repository. The
 ## Required Skills
 
 Before starting, load and follow these skills:
-- `codebase-analysis` - for the structured codebase analysis process and report template
+- `codebase-analysis` - for the structured codebase analysis process only (note: this prompt's "Report Structure" section overrides any report/template instructions from the skill)
 - `technical-context-discovery` - to understand project conventions, architecture patterns, and established practices
 - `code-review` - for code quality standards, best practices verification, and security considerations
 
PATCH

echo "Gold patch applied."

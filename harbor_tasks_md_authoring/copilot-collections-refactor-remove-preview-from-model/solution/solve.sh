#!/usr/bin/env bash
set -euo pipefail

cd /workspace/copilot-collections

# Idempotency guard
if grep -qF "model: \"Claude Opus 4.5\"" ".github/prompts/implement-ui.prompt.md" && grep -qF "model: \"Claude Opus 4.5\"" ".github/prompts/implement.prompt.md" && grep -qF "model: \"Claude Opus 4.5\"" ".github/prompts/plan.prompt.md" && grep -qF "model: \"Claude Opus 4.5\"" ".github/prompts/research.prompt.md" && grep -qF "model: \"Claude Opus 4.5\"" ".github/prompts/review-ui.prompt.md" && grep -qF "model: \"Claude Opus 4.5\"" ".github/prompts/review.prompt.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/prompts/implement-ui.prompt.md b/.github/prompts/implement-ui.prompt.md
@@ -1,6 +1,6 @@
 ---
 agent: "tsh-frontend-software-engineer"
-model: "Claude Opus 4.5 (Preview)"
+model: "Claude Opus 4.5"
 description: "Implement UI feature according to the plan with iterative Figma verification until pixel-perfect."
 ---
 
diff --git a/.github/prompts/implement.prompt.md b/.github/prompts/implement.prompt.md
@@ -1,6 +1,6 @@
 ---
 agent: "tsh-software-engineer"
-model: "Claude Opus 4.5 (Preview)"
+model: "Claude Opus 4.5"
 description: "Implement feature according to the plan."
 ---
 
diff --git a/.github/prompts/plan.prompt.md b/.github/prompts/plan.prompt.md
@@ -1,6 +1,6 @@
 ---
 agent: "tsh-architect"
-model: "Claude Opus 4.5 (Preview)"
+model: "Claude Opus 4.5"
 description: "Prepare detailed implementation plan for given feature."
 ---
 
diff --git a/.github/prompts/research.prompt.md b/.github/prompts/research.prompt.md
@@ -1,6 +1,6 @@
 ---
 agent: "tsh-business-analyst"
-model: "Claude Opus 4.5 (Preview)"
+model: "Claude Opus 4.5"
 description: "Prepare a context for a specific task or feature from a business analysis perspective."
 ---
 
diff --git a/.github/prompts/review-ui.prompt.md b/.github/prompts/review-ui.prompt.md
@@ -1,6 +1,6 @@
 ---
 agent: "tsh-ui-reviewer"
-model: "Claude Opus 4.5 (Preview)"
+model: "Claude Opus 4.5"
 description: "Verify UI implementation against Figma designs using MCP tools."
 ---
 
diff --git a/.github/prompts/review.prompt.md b/.github/prompts/review.prompt.md
@@ -1,6 +1,6 @@
 ---
 agent: "tsh-code-reviewer"
-model: "Claude Opus 4.5 (Preview)"
+model: "Claude Opus 4.5"
 description: "Check the implementation against the plan and feature context."
 ---
 
PATCH

echo "Gold patch applied."

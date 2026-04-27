#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "date_added: 2026-03-18" "skills/advanced-evaluation/SKILL.md" && grep -qF "Detects attack vectors where attacker-controlled" "skills/agentic-actions-auditor/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/advanced-evaluation/SKILL.md b/skills/advanced-evaluation/SKILL.md
@@ -1,6 +1,9 @@
 ---
 name: advanced-evaluation
 description: This skill should be used when the user asks to "implement LLM-as-judge", "compare model outputs", "create evaluation rubrics", "mitigate evaluation bias", or mentions direct scoring, pairwise comparison, position bias, evaluation pipelines, or automated quality assessment.
+risk: safe
+source: community
+date_added: 2026-03-18
 ---
 
 # Advanced Evaluation
diff --git a/skills/agentic-actions-auditor/SKILL.md b/skills/agentic-actions-auditor/SKILL.md
@@ -1,6 +1,17 @@
 ---
 name: agentic-actions-auditor
-description: Audits GitHub Actions workflows for security vulnerabilities in AI agent integrations including Claude Code Action, Gemini CLI, OpenAI Codex, and GitHub AI Inference. Detects attack vectors where attacker-controlled input reaches AI agents running in CI/CD pipelines,...
+description: >
+  Audits GitHub Actions workflows for security
+  vulnerabilities in AI agent integrations 
+  including Claude Code Action, 
+  Gemini CLI, OpenAI Codex, and GitHub AI 
+  Inference. 
+  Detects attack vectors where attacker-controlled 
+  input reaches.
+  AI agents running in CI/CD pipelines.
+risk: safe
+source: community
+date_added: 2026-03-18
 ---
 
 # Agentic Actions Auditor
PATCH

echo "Gold patch applied."

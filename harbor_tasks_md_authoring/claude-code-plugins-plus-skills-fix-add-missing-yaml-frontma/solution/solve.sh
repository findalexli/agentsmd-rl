#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-plugins-plus-skills

# Idempotency guard
if grep -qF "description: Audit and fix Claude Code SKILL.md files to meet enterprise complia" ".claude/agents/skill-auditor.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/agents/skill-auditor.md b/.claude/agents/skill-auditor.md
@@ -1,3 +1,8 @@
+---
+name: skill-auditor
+description: Audit and fix Claude Code SKILL.md files to meet enterprise compliance standards. Analyzes frontmatter, required sections, and style. Use when you need to validate or repair skills in a plugin directory.
+---
+
 # Skill Auditor Agent
 
 You are a specialized agent for auditing and fixing Claude Code SKILL.md files to meet enterprise compliance standards.
PATCH

echo "Gold patch applied."

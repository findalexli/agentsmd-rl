#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marketingskills

# Idempotency guard
if grep -qF "These patterns are **Claude Code only** and must not be added to `SKILL.md` file" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -219,3 +219,36 @@ When using any skill from this repository:
 ## Skill Categories
 
 See `README.md` for the current list of skills organized by category. When adding new skills, follow the naming patterns of existing skills in that category.
+
+## Claude Code-Specific Enhancements
+
+These patterns are **Claude Code only** and must not be added to `SKILL.md` files directly, as skills are designed to be cross-agent compatible (Codex, Cursor, Windsurf, etc.). Apply them locally in your own project's `.claude/skills/` overrides instead.
+
+### Dynamic content injection with `!`command``
+
+Claude Code supports embedding shell commands in SKILL.md using `` !`command` `` syntax. When the skill is invoked, Claude Code runs the command and injects the output inline — the model sees the result, not the instruction.
+
+**Most useful application: auto-inject the product marketing context file**
+
+Instead of every skill telling the agent "go check if `.agents/product-marketing-context.md` exists and read it," you can inject it automatically:
+
+```markdown
+Product context: !`cat .agents/product-marketing-context.md 2>/dev/null || echo "No product context file found — ask the user about their product before proceeding."`
+```
+
+Place this at the top of a skill's body (after frontmatter) to make context available immediately without any file-reading step.
+
+**Other useful injections:**
+
+```markdown
+# Inject today's date for recency-sensitive skills
+Today's date: !`date +%Y-%m-%d`
+
+# Inject current git branch (useful for workflow skills)
+Current branch: !`git branch --show-current 2>/dev/null`
+
+# Inject recent commits for context
+Recent commits: !`git log --oneline -5 2>/dev/null`
+```
+
+**Why this is Claude Code-only**: Other agents that load skills will see the literal `` !`command` `` string rather than executing it, which would appear as garbled instructions. Keep cross-agent skill files free of this syntax.
PATCH

echo "Gold patch applied."

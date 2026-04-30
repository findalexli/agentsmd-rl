#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotency guard
if grep -qF "disable-model-invocation: true" ".claude/skills/pr-review/SKILL.md" && grep -qF "disable-model-invocation: true" ".claude/skills/resolve/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/pr-review/SKILL.md b/.claude/skills/pr-review/SKILL.md
@@ -1,4 +1,5 @@
 ---
+disable-model-invocation: true
 allowed-tools: Read, Skill, Bash, Grep, Glob
 argument-hint: [extra_context]
 description: Review a GitHub pull request, add review comments for issues found, and approve if no significant issues exist
diff --git a/.claude/skills/resolve/SKILL.md b/.claude/skills/resolve/SKILL.md
@@ -1,4 +1,5 @@
 ---
+disable-model-invocation: true
 allowed-tools: Skill, Read, Edit, Write, Glob, Grep, Bash
 argument-hint: [extra_context]
 description: Resolve PR review comments by fetching unresolved feedback and making necessary code changes
PATCH

echo "Gold patch applied."

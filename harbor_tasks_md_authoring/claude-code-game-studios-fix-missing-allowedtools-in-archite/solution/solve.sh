#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-game-studios

# Idempotency guard
if grep -qF "allowed-tools: Read, Glob, Grep, Write, Edit, Task, AskUserQuestion" ".claude/skills/architecture-decision/SKILL.md" && grep -qF "allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion, Task" ".claude/skills/story-done/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/architecture-decision/SKILL.md b/.claude/skills/architecture-decision/SKILL.md
@@ -3,7 +3,7 @@ name: architecture-decision
 description: "Creates an Architecture Decision Record (ADR) documenting a significant technical decision, its context, alternatives considered, and consequences. Every major technical choice should have an ADR."
 argument-hint: "[title] [--review full|lean|solo]"
 user-invocable: true
-allowed-tools: Read, Glob, Grep, Write, Task, AskUserQuestion
+allowed-tools: Read, Glob, Grep, Write, Edit, Task, AskUserQuestion
 ---
 
 When this skill is invoked:
diff --git a/.claude/skills/story-done/SKILL.md b/.claude/skills/story-done/SKILL.md
@@ -3,7 +3,7 @@ name: story-done
 description: "End-of-story completion review. Reads the story file, verifies each acceptance criterion against the implementation, checks for GDD/ADR deviations, prompts code review, updates story status to Complete, and surfaces the next ready story from the sprint."
 argument-hint: "[story-file-path] [--review full|lean|solo]"
 user-invocable: true
-allowed-tools: Read, Glob, Grep, Bash, Edit, AskUserQuestion, Task
+allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion, Task
 ---
 
 # Story Done
PATCH

echo "Gold patch applied."

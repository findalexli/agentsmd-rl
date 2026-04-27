#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-howto

# Idempotency guard
if grep -qF "- **Explanation**: Skill metadata occupies about 1% of the context window (fallb" ".claude/skills/lesson-quiz/references/question-bank.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/lesson-quiz/references/question-bank.md b/.claude/skills/lesson-quiz/references/question-bank.md
@@ -209,9 +209,9 @@
 ### Q5
 - **Category**: conceptual
 - **Question**: What is the approximate context budget allocated to skill metadata (Level 1)?
-- **Options**: A) 0.5% of context window | B) 2% of context window | C) 5% of context window | D) 10% of context window
+- **Options**: A) 0.5% of context window | B) 1% of context window | C) 5% of context window | D) 10% of context window
 - **Correct**: B
-- **Explanation**: Skill metadata occupies about 2% of the context window (fallback: 16,000 characters). This is configurable with `SLASH_COMMAND_TOOL_CHAR_BUDGET`.
+- **Explanation**: Skill metadata occupies about 1% of the context window (fallback: 8,000 characters). This is configurable with `SLASH_COMMAND_TOOL_CHAR_BUDGET`.
 - **Review**: Context budget section
 
 ### Q6
@@ -269,9 +269,9 @@
 ### Q2
 - **Category**: practical
 - **Question**: What is the priority order for agent definitions?
-- **Options**: A) Project > User > CLI | B) CLI > User > Project | C) User > Project > CLI | D) They all have equal priority
+- **Options**: A) Project > User > CLI | B) CLI > Project > User | C) User > Project > CLI | D) They all have equal priority
 - **Correct**: B
-- **Explanation**: CLI-defined agents (`--agents` flag) override User-level (`~/.claude/agents/`), which override Project-level (`.claude/agents/`).
+- **Explanation**: CLI-defined agents (`--agents` flag) override Project-level (`.claude/agents/`), which override User-level (`~/.claude/agents/`).
 - **Review**: File locations section
 
 ### Q3
PATCH

echo "Gold patch applied."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vibe-skills

# Idempotency guard
if grep -qF "**In OpenCode:** Use the `skill` tool. OpenCode natively supports skills from `." "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -2,6 +2,56 @@
 name: vibe
 description: Vibe Code Orchestrator (VCO) is a governed runtime entry that freezes requirements, plans XL-first execution, and enforces verification and phase cleanup.
 ---
+<EXTREMELY-IMPORTANT>
+If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.
+
+IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.
+
+This is not negotiable. This is not optional. You cannot rationalize your way out of this.
+</EXTREMELY-IMPORTANT>
+
+## Instruction Priority
+
+Vibe skills override default system prompt behavior, but **user instructions always take precedence**:
+
+1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
+2. **vibe skills** — override default system behavior where they conflict
+3. **Default system prompt** — lowest priority
+
+If CLAUDE.md, GEMINI.md, or AGENTS.md says "don't use TDD" and a skill says "always use TDD," follow the user's instructions. The user is in control.
+
+## How to Access Skills
+
+**In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded and presented to you—follow it directly. Never use the Read tool on skill files.
+
+**In Copilot CLI:** Use the `skill` tool. Skills are auto-discovered from installed plugins. The `skill` tool works the same as Claude Code's `Skill` tool.
+
+**In Gemini CLI:** Skills activate via the `activate_skill` tool. Gemini loads skill metadata at session start and activates the full content on demand.
+
+**In OpenCode:** Use the `skill` tool. OpenCode natively supports skills from `.claude/skills/`, `.opencode/skills/`, and `.agents/skills/`. Invoke via `skill({ name: "skill-name" })`.
+
+**In other environments:** Check your platform's documentation for how skills are loaded.
+
+
+## Red Flags
+
+These thoughts mean STOP—you're rationalizing:
+
+| Thought | Reality |
+|---------|---------|
+| "This is just a simple question" | Questions are tasks. Check for skills. |
+| "I need more context first" | Skill check comes BEFORE clarifying questions. |
+| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
+| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
+| "Let me gather information first" | Skills tell you HOW to gather information. |
+| "This doesn't need a formal skill" | If a skill exists, use it. |
+| "I remember this skill" | Skills evolve. Read current version. |
+| "This doesn't count as a task" | Action = task. Check for skills. |
+| "The skill is overkill" | Simple things become complex. Use it. |
+| "I'll just do this one thing first" | Check BEFORE doing anything. |
+| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
+| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |
+
 
 # Vibe Governed Runtime
 
PATCH

echo "Gold patch applied."

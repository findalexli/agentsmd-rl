#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tt-metal

# Idempotency guard
if grep -qF "**MANDATORY**: Before dispatching agents or taking action for the triggers below" "tt_metal/tt-llk/.claude/CLAUDE.md" && grep -qF "tt_metal/tt-llk/.claude/skills/arch-lookup/SKILL.md" "tt_metal/tt-llk/.claude/skills/arch-lookup/SKILL.md" && grep -qF "tt_metal/tt-llk/.claude/skills/debug-kernel/SKILL.md" "tt_metal/tt-llk/.claude/skills/debug-kernel/SKILL.md" && grep -qF "tt_metal/tt-llk/.claude/skills/port-kernel/SKILL.md" "tt_metal/tt-llk/.claude/skills/port-kernel/SKILL.md" && grep -qF "tt_metal/tt-llk/.claude/skills/run-test/SKILL.md" "tt_metal/tt-llk/.claude/skills/run-test/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/tt_metal/tt-llk/.claude/CLAUDE.md b/tt_metal/tt-llk/.claude/CLAUDE.md
@@ -32,16 +32,16 @@ Execution model: RISC-V cores push instructions to corresponding coprocessor thr
 
 ## Skills & Agents
 
-**MANDATORY**: Before dispatching agents or taking action for the triggers below, you MUST first read the corresponding skill file with the `Read` tool and follow the instructions inside it. Never manually dispatch sage agents without first loading the relevant skill — the skill defines the correct orchestration pattern, prompt structure, and quality checklist.
+**MANDATORY**: Before dispatching agents or taking action for the triggers below, you MUST first invoke the corresponding skill (or `Read` its `SKILL.md`) and follow the instructions inside it. Never manually dispatch sage agents without first loading the relevant skill — the skill defines the correct orchestration pattern, prompt structure, and quality checklist.
 
-**Note:** Skills live in `.claude/skills/` relative to this file. Because tt-llk is a subdirectory of the tt-metal git repo, the `Skill` tool cannot discover them. Use `Read(".claude/skills/<name>.md")` instead.
+**Note:** Skills live in `.claude/skills/<name>/SKILL.md` relative to this file. Claude Code auto-discovers them when launched from inside `tt-llk/` (nested-subdirectory discovery). If the `Skill` tool doesn't list them, fall back to `Read(".claude/skills/<name>/SKILL.md")`.
 
-| Trigger | Skill file to read | What it does |
-|---------|-------------------|--------------|
-| Architecture, instruction, or LLK questions | `.claude/skills/arch-lookup.md` | Orchestrates sage agents in parallel, aggregates results |
-| Running tests | `.claude/skills/run-test.md` | Dispatches llk-test-runner with correct scenario flags |
-| Debugging kernel errors | `.claude/skills/debug-kernel.md` | Dispatches llk-debugger with inferred arch/kernel type |
-| Porting kernels between architectures | `.claude/skills/port-kernel.md` | Launches source + target sages, reads test harness |
+| Trigger | Skill | What it does |
+|---------|-------|--------------|
+| Architecture, instruction, or LLK questions | `arch-lookup` (`.claude/skills/arch-lookup/SKILL.md`) | Orchestrates sage agents in parallel, aggregates results |
+| Running tests | `run-test` (`.claude/skills/run-test/SKILL.md`) | Dispatches llk-test-runner with correct scenario flags |
+| Debugging kernel errors | `debug-kernel` (`.claude/skills/debug-kernel/SKILL.md`) | Dispatches llk-debugger with inferred arch/kernel type |
+| Porting kernels between architectures | `port-kernel` (`.claude/skills/port-kernel/SKILL.md`) | Launches source + target sages, reads test harness |
 
 Trigger examples for `arch-lookup`:
 - "How does SFPMAD work?", "What is BroadcastType?", "How does unpack handle Float16?"
diff --git a/tt_metal/tt-llk/.claude/skills/arch-lookup/SKILL.md b/tt_metal/tt-llk/.claude/skills/arch-lookup/SKILL.md

diff --git a/tt_metal/tt-llk/.claude/skills/debug-kernel/SKILL.md b/tt_metal/tt-llk/.claude/skills/debug-kernel/SKILL.md

diff --git a/tt_metal/tt-llk/.claude/skills/port-kernel/SKILL.md b/tt_metal/tt-llk/.claude/skills/port-kernel/SKILL.md

diff --git a/tt_metal/tt-llk/.claude/skills/run-test/SKILL.md b/tt_metal/tt-llk/.claude/skills/run-test/SKILL.md

PATCH

echo "Gold patch applied."

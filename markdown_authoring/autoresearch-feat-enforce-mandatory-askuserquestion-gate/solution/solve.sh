#!/usr/bin/env bash
set -euo pipefail

cd /workspace/autoresearch

# Idempotency guard
if grep -qF "**CRITICAL: If ANY critical field is missing (Goal, Scope, Metric, Direction, or" ".claude/skills/autoresearch/SKILL.md" && grep -qF "**CRITICAL \u2014 BLOCKING PREREQUISITE:** If `/autoresearch:debug` is invoked withou" ".claude/skills/autoresearch/references/debug-workflow.md" && grep -qF "**CRITICAL \u2014 BLOCKING PREREQUISITE:** If `/autoresearch:fix` is invoked without " ".claude/skills/autoresearch/references/fix-workflow.md" && grep -qF "**CRITICAL \u2014 BLOCKING PREREQUISITE:** If no goal is provided inline, you MUST us" ".claude/skills/autoresearch/references/plan-workflow.md" && grep -qF "**CRITICAL \u2014 BLOCKING PREREQUISITE:** If `/autoresearch:security` is invoked wit" ".claude/skills/autoresearch/references/security-workflow.md" && grep -qF "**CRITICAL \u2014 BLOCKING PREREQUISITE:** If `/autoresearch:ship` is invoked without" ".claude/skills/autoresearch/references/ship-workflow.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/autoresearch/SKILL.md b/.claude/skills/autoresearch/SKILL.md
@@ -10,6 +10,27 @@ Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch).
 
 **Core idea:** You are an autonomous agent. Modify → Verify → Keep/Discard → Repeat.
 
+## MANDATORY: Interactive Setup Gate
+
+**CRITICAL — READ THIS FIRST BEFORE ANY ACTION:**
+
+For ALL commands (`/autoresearch`, `/autoresearch:plan`, `/autoresearch:debug`, `/autoresearch:fix`, `/autoresearch:security`, `/autoresearch:ship`):
+
+1. **Check if the user provided ALL required context inline** (Goal, Scope, Metric, flags, etc.)
+2. **If ANY required context is missing → you MUST use `AskUserQuestion` to collect it BEFORE proceeding to any execution phase.** DO NOT skip this step. DO NOT proceed without user input.
+3. Each subcommand's reference file has an "Interactive Setup" section — follow it exactly when context is missing.
+
+| Command | Required Context | If Missing → Ask |
+|---------|-----------------|-----------------|
+| `/autoresearch` | Goal, Scope, Metric, Direction, Verify | Batch 1 (4 questions) + Batch 2 (3 questions) from Setup Phase below |
+| `/autoresearch:plan` | Goal | Ask via `AskUserQuestion` per `references/plan-workflow.md` |
+| `/autoresearch:debug` | Issue/Symptom, Scope | 4 batched questions per `references/debug-workflow.md` |
+| `/autoresearch:fix` | Target, Scope | 4 batched questions per `references/fix-workflow.md` |
+| `/autoresearch:security` | Scope, Depth | 3 batched questions per `references/security-workflow.md` |
+| `/autoresearch:ship` | What/Type, Mode | 3 batched questions per `references/ship-workflow.md` |
+
+**YOU MUST NOT start any loop, phase, or execution without completing interactive setup when context is missing. This is a BLOCKING prerequisite.**
+
 ## Subcommands
 
 | Subcommand | Purpose |
@@ -258,7 +279,7 @@ After N iterations Claude stops and prints a final summary with baseline → cur
 
 **If the user provides Goal, Scope, Metric, and Verify inline** → extract them and proceed to step 5.
 
-**If any critical field is missing** → use `AskUserQuestion` to collect them interactively:
+**CRITICAL: If ANY critical field is missing (Goal, Scope, Metric, Direction, or Verify), you MUST use `AskUserQuestion` to collect them interactively. DO NOT proceed to The Loop or any execution phase without completing this setup. This is a BLOCKING prerequisite.**
 
 ### Interactive Setup (when invoked without full config)
 
@@ -285,7 +306,7 @@ Use a SINGLE `AskUserQuestion` call with these 4 questions:
 
 **After Batch 2:** Dry-run the verify command. If it fails, ask user to fix or choose a different command. If it passes, proceed with launch choice.
 
-**IMPORTANT:** Always batch questions — never ask one at a time. Users should see all config choices together for full context.
+**IMPORTANT:** You MUST call `AskUserQuestion` with batched questions — never ask one at a time, and never skip this step. Users should see all config choices together for full context. DO NOT proceed to Setup Steps or The Loop without completing interactive setup.
 
 ### Setup Steps (after config is complete)
 
diff --git a/.claude/skills/autoresearch/references/debug-workflow.md b/.claude/skills/autoresearch/references/debug-workflow.md
@@ -26,13 +26,15 @@ Scope: src/api/**/*.ts
 Symptom: API returns 500 on POST /users
 ```
 
-## Interactive Setup (when invoked without flags)
+## PREREQUISITE: Interactive Setup (when invoked without flags)
 
-If `/autoresearch:debug` is invoked without `--scope` or `--symptom`, use `AskUserQuestion` to gather full context in ONE batched call before investigating. Scan the codebase first (run tests, lint, typecheck) to detect existing failures and provide smart defaults.
+**CRITICAL — BLOCKING PREREQUISITE:** If `/autoresearch:debug` is invoked without `--scope` or `--symptom`, you MUST use `AskUserQuestion` to gather full context BEFORE proceeding to ANY phase. DO NOT skip this step. DO NOT jump to Phase 1 without completing interactive setup.
+
+Scan the codebase first (run tests, lint, typecheck) to detect existing failures and provide smart defaults.
 
 **Single batched call — all 4 questions at once:**
 
-Use ONE `AskUserQuestion` call with all 4 questions:
+You MUST call `AskUserQuestion` with all 4 questions in ONE call:
 
 | # | Header | Question | Options (from codebase scan) |
 |---|--------|----------|------------------------------|
@@ -60,6 +62,8 @@ If `--scope`, `--symptom`, or `--fix` flags are provided, skip the interactive s
 
 ## Phase 1: Gather — Symptoms & Context
 
+**STOP: Have you completed the Interactive Setup above?** If invoked without `--scope`/`--symptom` flags, you MUST complete the `AskUserQuestion` call above BEFORE entering this phase.
+
 Collect everything known about the problem before investigating.
 
 **If user provides symptoms:**
diff --git a/.claude/skills/autoresearch/references/fix-workflow.md b/.claude/skills/autoresearch/references/fix-workflow.md
@@ -27,15 +27,15 @@ Scope: src/**/*.ts
 Guard: npm run typecheck
 ```
 
-## Interactive Setup (when invoked without flags)
+## PREREQUISITE: Interactive Setup (when invoked without flags)
 
-If `/autoresearch:fix` is invoked without explicit `--target`, `--guard`, or `--scope`, first auto-detect all failures (run tests, typecheck, lint, build), then use `AskUserQuestion` with ALL questions batched in a single call.
+**CRITICAL — BLOCKING PREREQUISITE:** If `/autoresearch:fix` is invoked without explicit `--target`, `--guard`, or `--scope`, you MUST first auto-detect all failures, then use `AskUserQuestion` to gather user input BEFORE proceeding to ANY phase. DO NOT skip this step. DO NOT jump to Phase 1 without completing interactive setup.
 
 **Pre-scan:** Run test suite, type checker, linter, and build to detect failures. Present summary in the first question.
 
 **Single batched call — all 4 questions at once:**
 
-Use ONE `AskUserQuestion` call with all 4 questions:
+You MUST call `AskUserQuestion` with all 4 questions in ONE call:
 
 | # | Header | Question | Options (from auto-detection) |
 |---|--------|----------|-------------------------------|
@@ -64,6 +64,8 @@ If the user provides `--target`, `--guard`, `--scope`, or `--from-debug` flags,
 
 ## Phase 1: Detect — What's Broken?
 
+**STOP: Have you completed the Interactive Setup above?** If invoked without `--target`/`--guard`/`--scope` flags, you MUST complete the `AskUserQuestion` call above BEFORE entering this phase.
+
 Auto-detect the failure domain from context, or accept explicit target.
 
 **Detection algorithm:**
diff --git a/.claude/skills/autoresearch/references/plan-workflow.md b/.claude/skills/autoresearch/references/plan-workflow.md
@@ -13,7 +13,7 @@ Convert a textual goal into a validated, ready-to-execute autoresearch configura
 
 ### Phase 1: Capture Goal
 
-If no goal provided, ask:
+**CRITICAL — BLOCKING PREREQUISITE:** If no goal is provided inline, you MUST use `AskUserQuestion` to capture it. DO NOT skip this step or proceed to Phase 2 without a goal.
 
 ```
 AskUserQuestion:
diff --git a/.claude/skills/autoresearch/references/security-workflow.md b/.claude/skills/autoresearch/references/security-workflow.md
@@ -28,13 +28,13 @@ Scope: src/api/**/*.ts, src/middleware/**/*.ts
 Focus: authentication and authorization flows
 ```
 
-## Interactive Setup (when invoked without flags)
+## PREREQUISITE: Interactive Setup (when invoked without flags)
 
-If `/autoresearch:security` is invoked without `--diff`, scope, or focus, scan the codebase first (detect tech stack, API routes, auth patterns), then use `AskUserQuestion` with ALL questions batched.
+**CRITICAL — BLOCKING PREREQUISITE:** If `/autoresearch:security` is invoked without `--diff`, scope, or focus, you MUST scan the codebase first, then use `AskUserQuestion` to gather user input BEFORE proceeding to ANY phase. DO NOT skip this step.
 
 **Single batched call — all 3 questions at once:**
 
-Use ONE `AskUserQuestion` call with all 3 questions:
+You MUST call `AskUserQuestion` with all 3 questions in ONE call:
 
 | # | Header | Question | Options (from codebase scan) |
 |---|--------|----------|------------------------------|
diff --git a/.claude/skills/autoresearch/references/ship-workflow.md b/.claude/skills/autoresearch/references/ship-workflow.md
@@ -28,13 +28,13 @@ Target: src/features/auth/**
 Destination: production
 ```
 
-## Interactive Setup (when invoked without flags)
+## PREREQUISITE: Interactive Setup (when invoked without flags)
 
-If `/autoresearch:ship` is invoked without `--type` or target, scan for staged changes, open PRs, and recent commits, then use `AskUserQuestion` with ALL questions batched.
+**CRITICAL — BLOCKING PREREQUISITE:** If `/autoresearch:ship` is invoked without `--type` or target, you MUST scan for staged changes, open PRs, and recent commits, then use `AskUserQuestion` to gather user input BEFORE proceeding to ANY phase. DO NOT skip this step.
 
 **Single batched call — all 3 questions at once:**
 
-Use ONE `AskUserQuestion` call with all 3 questions:
+You MUST call `AskUserQuestion` with all 3 questions in ONE call:
 
 | # | Header | Question | Options (from context scan) |
 |---|--------|----------|----------------------------|
PATCH

echo "Gold patch applied."

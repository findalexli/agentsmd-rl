#!/usr/bin/env bash
set -euo pipefail

cd /workspace/moai-adk

# Idempotency guard
if grep -qF "If `--team` flag was parsed AND `${CLAUDE_SKILL_DIR}/team/<name>.md` exists for " ".claude/skills/moai/SKILL.md" && grep -qF "If `--team` flag was parsed AND `${CLAUDE_SKILL_DIR}/team/<name>.md` exists for " "internal/template/templates/.claude/skills/moai/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/moai/SKILL.md b/.claude/skills/moai/SKILL.md
@@ -107,21 +107,21 @@ Purpose: Create comprehensive specification documents using EARS format with Res
 Phases: Deep Research (research.md) -> SPEC Planning -> Annotation Cycle (1-6 iterations) -> SPEC Creation
 Agents: manager-spec (primary), Explore (research), manager-git (conditional)
 Flags: --worktree, --branch, --resume SPEC-XXX, --team, --no-issue
-For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/plan.md
+For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/plan.md (team mode: ${CLAUDE_SKILL_DIR}/team/plan.md)
 
 ### run - DDD/TDD Implementation
 
 Purpose: Implement SPEC requirements through configured development methodology.
 Agents: manager-strategy, manager-ddd or manager-tdd (per quality.yaml), manager-quality, manager-git
 Flags: --resume SPEC-XXX, --team
-For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/run.md
+For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/run.md (team mode: ${CLAUDE_SKILL_DIR}/team/run.md)
 
 ### sync - Documentation Sync and PR
 
 Purpose: Synchronize documentation with code changes and prepare pull requests.
 Agents: manager-docs (primary), manager-quality, manager-git
 Modes: auto, force, status, project. Flags: --merge, --skip-mx
-For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/sync.md
+For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/sync.md (team mode: ${CLAUDE_SKILL_DIR}/team/sync.md)
 
 ### gate - Pre-Commit Quality Gate
 
@@ -255,7 +255,7 @@ All AskUserQuestion calls throughout MoAI workflows MUST follow these rules:
 - Every option MUST include a detailed description explaining what it does and its implications
 
 Step 3 - Load Workflow Details:
-Read the corresponding workflows/<name>.md file for detailed orchestration instructions.
+If `--team` flag was parsed AND `${CLAUDE_SKILL_DIR}/team/<name>.md` exists for the target subcommand, read the team workflow file instead of the solo workflow. Otherwise read `workflows/<name>.md`. The Quick Reference section above shows both paths for each subcommand that supports team mode.
 
 Step 4 - Read Configuration:
 Load relevant configuration from .moai/config/config.yaml and section files as needed.
diff --git a/internal/template/templates/.claude/skills/moai/SKILL.md b/internal/template/templates/.claude/skills/moai/SKILL.md
@@ -107,21 +107,21 @@ Purpose: Create comprehensive specification documents using EARS format with Res
 Phases: Deep Research (research.md) -> SPEC Planning -> Annotation Cycle (1-6 iterations) -> SPEC Creation
 Agents: manager-spec (primary), Explore (research), manager-git (conditional)
 Flags: --worktree, --branch, --resume SPEC-XXX, --team, --no-issue
-For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/plan.md
+For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/plan.md (team mode: ${CLAUDE_SKILL_DIR}/team/plan.md)
 
 ### run - DDD/TDD Implementation
 
 Purpose: Implement SPEC requirements through configured development methodology.
 Agents: manager-strategy, manager-ddd or manager-tdd (per quality.yaml), manager-quality, manager-git
 Flags: --resume SPEC-XXX, --team
-For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/run.md
+For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/run.md (team mode: ${CLAUDE_SKILL_DIR}/team/run.md)
 
 ### sync - Documentation Sync and PR
 
 Purpose: Synchronize documentation with code changes and prepare pull requests.
 Agents: manager-docs (primary), manager-quality, manager-git
 Modes: auto, force, status, project. Flags: --merge, --skip-mx
-For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/sync.md
+For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/sync.md (team mode: ${CLAUDE_SKILL_DIR}/team/sync.md)
 
 ### gate - Pre-Commit Quality Gate
 
@@ -255,7 +255,7 @@ All AskUserQuestion calls throughout MoAI workflows MUST follow these rules:
 - Every option MUST include a detailed description explaining what it does and its implications
 
 Step 3 - Load Workflow Details:
-Read the corresponding workflows/<name>.md file for detailed orchestration instructions.
+If `--team` flag was parsed AND `${CLAUDE_SKILL_DIR}/team/<name>.md` exists for the target subcommand, read the team workflow file instead of the solo workflow. Otherwise read `workflows/<name>.md`. The Quick Reference section above shows both paths for each subcommand that supports team mode.
 
 Step 4 - Read Configuration:
 Load relevant configuration from .moai/config/config.yaml and section files as needed.
@@ -282,3 +282,42 @@ Use AskUserQuestion to present the user with logical next actions based on the c
 
 Version: 2.6.0
 Last Updated: 2026-02-25
+
+<!-- moai:evolvable-start id="rationalizations" -->
+## Common Rationalizations
+
+| Rationalization | Reality |
+|---|---|
+| "I will just implement this directly, delegation is overhead" | MoAI is an orchestrator. Direct implementation bypasses the quality gates agents enforce. |
+| "The user's intent is obvious, no need for a Socratic interview" | Ambiguous verbs (clean, fix, improve) almost always produce wrong scope. Rule 5 exists because obvious is often wrong. |
+| "This is a small change, Approach-First is unnecessary" | Small changes still touch files the user cares about. One sentence of approach costs nothing and prevents rework. |
+| "I can run /moai run without a SPEC, it is just a tweak" | Without a SPEC, there is no acceptance criterion to check. Every run without a SPEC silently degrades quality tracking. |
+| "Parallel agents will just race, sequential is safer" | Independent tool calls are explicitly required to run in parallel. Sequentializing them wastes user time. |
+| "I will respond in English since it is technical" | Conversation language is a HARD rule. User-facing output must match the configured language, always. |
+
+<!-- moai:evolvable-end -->
+
+<!-- moai:evolvable-start id="red-flags" -->
+## Red Flags
+
+- MoAI writes code directly instead of delegating to a specialized agent
+- Response in English when conversation_language is not English
+- Multiple independent tool calls executed sequentially in separate messages
+- AskUserQuestion with more than 4 options or containing emoji
+- Agent invocation prompt contains absolute paths to the main project when isolation is worktree
+- /moai run executed without a corresponding SPEC-XXX document
+
+<!-- moai:evolvable-end -->
+
+<!-- moai:evolvable-start id="verification" -->
+## Verification
+
+- [ ] User-facing response language matches conversation_language from language.yaml
+- [ ] Every independent tool call was launched in parallel (one message, multiple tool blocks)
+- [ ] Agent selection trace documents why this agent, not another, was chosen
+- [ ] No XML tags visible in user-facing output
+- [ ] For non-trivial tasks, approach was explained and approved before code changes
+- [ ] SPEC-ID is referenced when /moai run, /moai sync, or /moai fix is invoked
+- [ ] TodoList used to decompose multi-file changes (3+ files)
+
+<!-- moai:evolvable-end -->
PATCH

echo "Gold patch applied."

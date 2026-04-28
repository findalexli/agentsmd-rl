#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mastra

# Idempotency guard
if grep -qF "- **E2E Tests for Studio** (`.claude/skills/e2e-tests-studio/SKILL.md`) \u2014 REQUIR" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -74,6 +74,35 @@ Mastra is a modular AI framework built around central orchestration with pluggab
 - **Workflows** (`workflows/`) - Step-based execution with suspend/resume.
 - **Storage** (`storage/`) - Pluggable backends with shared interfaces.
 
+## Commands
+
+Reusable command prompts are available in `.claude/commands/`. All agents should read and follow the relevant command file when performing these tasks.
+
+- **Changeset** (`.claude/commands/changeset.md`) — Create a changeset using the CLI for changelog generation.
+- **Commit** (`.claude/commands/commit.md`) — Commit work using conventional commits with a concise message, then push.
+- **Document** (`.claude/commands/document.md`) — Examine a GitHub issue and write documentation for it.
+- **Bulk Issue Solver** (`.claude/commands/gh-bulk-issues.md`) — Orchestrate parallel headless instances to debug and fix multiple GitHub issues simultaneously.
+- **Debug Issue** (`.claude/commands/gh-debug-issue.md`) — Examine and debug a GitHub issue using the GH CLI.
+- **Fix CI** (`.claude/commands/gh-fix-ci.md`) — Diagnose and fix GitHub Actions CI failures for the current branch's PR.
+- **Fix Lint** (`.claude/commands/gh-fix-lint.md`) — Fix linting and formatting issues for a GitHub PR branch.
+- **New PR** (`.claude/commands/gh-new-pr.md`) — Open a PR for the current branch using the GH CLI.
+- **PR Comments** (`.claude/commands/gh-pr-comments.md`) — View and handle PR review comments.
+- **Make Moves** (`.claude/commands/make-moves.md`) — Examine a GitHub issue and implement the fix as an engineer on the Mastra framework.
+- **PR** (`.claude/commands/pr.md`) — Create a changeset and open a PR for the current branch.
+- **Ralph Plan** (`.claude/commands/ralph-plan.md`) — Interactive assistant for building focused ralph-loop commands.
+
+## Skills
+
+This repository includes domain-specific guidance as skills in `.claude/skills/`. All agents should read the relevant skill file before performing work in that area.
+
+- **E2E Tests for Studio** (`.claude/skills/e2e-tests-studio/SKILL.md`) — REQUIRED when modifying any file in `packages/playground-ui` or `packages/playground`. Covers Playwright E2E test generation that validates product behavior.
+- **Mastra Docs** (`.claude/skills/mastra-docs/SKILL.md`) — Guidelines for writing or editing Mastra documentation.
+- **React Best Practices** (`.claude/skills/react-best-practices/SKILL.md`) — React performance optimization patterns. Read when writing, reviewing, or refactoring React components.
+- **Tailwind Best Practices** (`.claude/skills/tailwind-best-practices/SKILL.md`) — Tailwind CSS and design-system guidelines for `packages/playground-ui` and `packages/playground`.
+- **Mastra Smoke Test** (`.claude/skills/mastra-smoke-test/SKILL.md`) — Procedures for smoke testing Mastra projects locally or against staging/production.
+- **Smoke Test** (`.claude/skills/smoke-test/SKILL.md`) — Creating a Mastra project with `create-mastra` and smoke testing the studio in Chrome.
+- **Ralph Plan** (`.claude/skills/ralph-plan/SKILL.md`) — Interactive planning assistant for building ralph-loop commands.
+
 ## Enterprise Edition (EE) licensing
 
 - Any directory named `ee/` is licensed under the Mastra Enterprise License.
PATCH

echo "Gold patch applied."

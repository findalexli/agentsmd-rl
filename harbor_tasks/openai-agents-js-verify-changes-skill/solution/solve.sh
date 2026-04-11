#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openai-agents-js

# Idempotent: skip if already applied
if grep -q 'verify-changes' AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.codex/skills/verify-changes/SKILL.md b/.codex/skills/verify-changes/SKILL.md
new file mode 100644
index 000000000..591dc4f5f
--- /dev/null
+++ b/.codex/skills/verify-changes/SKILL.md
@@ -0,0 +1,36 @@
+---
+name: verify-changes
+description: Run all mandatory verification steps for code changes in the OpenAI Agents JS monorepo.
+---
+
+# Verify Changes
+
+## Overview
+
+Ensure work is only marked complete after installing dependencies, building, linting, type checking, and tests pass. Use this skill whenever wrapping up a task, before opening a PR, or when asked to confirm that changes are ready to hand off.
+
+## Quick start
+
+1. Keep this skill at `./.codex/skills/verify-changes` so it loads automatically for the repository.
+2. macOS/Linux: `bash .codex/skills/verify-changes/scripts/run.sh`.
+3. Windows: `powershell -ExecutionPolicy Bypass -File .codex/skills/verify-changes/scripts/run.ps1`.
+4. If any command fails, fix the issue, rerun the script, and report the failing output.
+5. Confirm completion only when all commands succeed with no remaining issues.
+
+## Manual workflow
+
+- Run from the repository root in this order: `pnpm i`, `pnpm build`, `pnpm -r build-check`, `pnpm lint`, `pnpm test`.
+- Do not skip steps; stop and fix issues immediately when a command fails.
+- Re-run the full stack after applying fixes so the commands execute in the required order.
+
+## Resources
+
+### scripts/run.sh
+
+- Executes the full verification sequence with fail-fast semantics.
+- Prefer this entry point to ensure the commands always run in the correct order from the repo root.
+
+### scripts/run.ps1
+
+- Windows-friendly wrapper that runs the same verification sequence with fail-fast semantics.
+- Use from PowerShell with execution policy bypass if required by your environment.
diff --git a/.codex/skills/verify-changes/scripts/run.ps1 b/.codex/skills/verify-changes/scripts/run.ps1
new file mode 100644
index 000000000..32b3d1d47
--- /dev/null
+++ b/.codex/skills/verify-changes/scripts/run.ps1
@@ -0,0 +1,40 @@
+Set-StrictMode -Version Latest
+$ErrorActionPreference = "Stop"
+
+$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
+$repoRoot = $null
+
+try {
+    $repoRoot = (& git -C $scriptDir rev-parse --show-toplevel 2>$null)
+} catch {
+    $repoRoot = $null
+}
+
+if (-not $repoRoot) {
+    $repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..\..")
+}
+
+Set-Location $repoRoot
+
+function Invoke-PnpmStep {
+    param(
+        [Parameter(Mandatory = $true)][string[]]$Args
+    )
+
+    $commandText = "pnpm " + ($Args -join " ")
+    Write-Host "Running $commandText..."
+    & pnpm @Args
+
+    if ($LASTEXITCODE -ne 0) {
+        Write-Error "verify-changes: $commandText failed with exit code $LASTEXITCODE."
+        exit $LASTEXITCODE
+    }
+}
+
+Invoke-PnpmStep -Args @("i")
+Invoke-PnpmStep -Args @("build")
+Invoke-PnpmStep -Args @("-r", "build-check")
+Invoke-PnpmStep -Args @("lint")
+Invoke-PnpmStep -Args @("test")
+
+Write-Host "verify-changes: all commands passed."
diff --git a/.codex/skills/verify-changes/scripts/run.sh b/.codex/skills/verify-changes/scripts/run.sh
new file mode 100755
index 000000000..d9c4bf9db
--- /dev/null
+++ b/.codex/skills/verify-changes/scripts/run.sh
@@ -0,0 +1,27 @@
+#!/usr/bin/env bash
+set -euo pipefail
+
+SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
+if command -v git >/dev/null 2>&1; then
+  REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel 2>/dev/null || true)"
+fi
+REPO_ROOT="${REPO_ROOT:-$(cd "${SCRIPT_DIR}/../../../.." && pwd)}"
+
+cd "${REPO_ROOT}"
+
+echo "Running pnpm i..."
+pnpm i
+
+echo "Running pnpm build..."
+pnpm build
+
+echo "Running pnpm -r build-check..."
+pnpm -r build-check
+
+echo "Running pnpm lint..."
+pnpm lint
+
+echo "Running pnpm test..."
+pnpm test
+
+echo "verify-changes: all commands passed."
diff --git a/AGENTS.md b/AGENTS.md
index 0cff11f1f..1d339a9fe 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -7,19 +7,25 @@ This guide helps new contributors get started with the OpenAI Agents JS monorepo
 ## ExecPlans

 When writing complex features or significant refactors, use an ExecPlan (as described in .agent/PLANS.md) from design to implementation.
+Call out potential backward compatibility or public API risks in your plan and confirm the approach when changes could impact package consumers.

 ## Table of Contents

-1.  [Overview](#overview)
-2.  [Repo Structure & Important Files](#repo-structure--important-files)
-3.  [Testing & Automated Checks](#testing--automated-checks)
-4.  [Repo-Specific Utilities](#repo-specific-utilities)
-5.  [Style, Linting & Type Checking](#style-linting--type-checking)
-6.  [Development Workflow](#development-workflow)
-7.  [Pull Request & Commit Guidelines](#pull-request--commit-guidelines)
-8.  [Review Process & What Reviewers Look For](#review-process--what-reviewers-look-for)
-9.  [Tips for Navigating the Repo](#tips-for-navigating-the-repo)
-10. [Prerequisites](#prerequisites)
+1.  [Mandatory Skill Usage](#mandatory-skill-usage)
+2.  [Overview](#overview)
+3.  [Repo Structure & Important Files](#repo-structure--important-files)
+4.  [Testing & Automated Checks](#testing--automated-checks)
+5.  [Repo-Specific Utilities](#repo-specific-utilities)
+6.  [Style, Linting & Type Checking](#style-linting--type-checking)
+7.  [Development Workflow](#development-workflow)
+8.  [Pull Request & Commit Guidelines](#pull-request--commit-guidelines)
+9.  [Review Process & What Reviewers Look For](#review-process--what-reviewers-look-for)
+10. [Tips for Navigating the Repo](#tips-for-navigating-the-repo)
+11. [Prerequisites](#prerequisites)
+
+## Mandatory Skill Usage
+
+Always load and use the `$verify-changes` skill immediately after any code change and before you consider the work complete. It executes the mandatory verification stack from the repository root; rerun the stack after fixing failures.

 ## Overview

@@ -38,7 +44,7 @@ The OpenAI Agents JS repository is a pnpm-managed monorepo that provides:
 ## Repo Structure & Important Files

 - `packages/agents-core/`, `packages/agents-openai/`, `packages/agents-realtime/`, `packages/agents-extensions/`: Each has its own `package.json`, `src/`, `test/`, and build scripts.
-- `docs/`: Documentation source; develop with `pnpm docs:dev` or build with `pnpm docs:build`.
+- `docs/`: Documentation source; develop with `pnpm docs:dev` or build with `pnpm docs:build`. Translated docs under `docs/src/content/docs/ja`, `docs/src/content/docs/ko`, and `docs/src/content/docs/zh` are generated via `pnpm docs:translate`; do not edit them manually.
 - `examples/`: Subdirectories (e.g. `basic`, `agent-patterns`) with their own `package.json` and start scripts.
 - `scripts/dev.mts`: Runs concurrent build-watchers and the docs dev server (`pnpm dev`).
 - `scripts/embedMeta.ts`: Generates `src/metadata.ts` for each package before build.
@@ -55,6 +61,8 @@ The OpenAI Agents JS repository is a pnpm-managed monorepo that provides:

 Before submitting changes, ensure all checks pass and augment tests when you touch code:

+After any code modification, invoke the `$verify-changes` skill to run the required verification stack from the repository root. Rerun the full stack after fixes.
+
 - Add or update unit tests for any code change unless it is truly infeasible; if something prevents adding tests, explain why in the PR.

 ### Unit Tests and Type Checking
@@ -110,11 +118,7 @@ See [this README](integration-tests/README.md) for details.

 ### Mandatory Local Run Order

-For every code change, run the full validation sequence locally:
-
-```bash
-pnpm lint && pnpm build && pnpm -r build-check && pnpm test
-```
+For every code change, run the full validation sequence locally via the `$verify-changes` skill; do not skip any step or change the order.

 ### Pre-commit Hooks

@@ -171,10 +175,7 @@ pnpm lint && pnpm build && pnpm -r build-check && pnpm test
     git checkout -b feat/<short-description>
     ```
 3.  Make changes and add/update unit tests in `packages/<pkg>/test` unless doing so is truly infeasible.
-4.  Run all checks (in this order):
-    ```bash
-    pnpm lint && pnpm build && pnpm -r build-check && pnpm test
-    ```
+4.  Run all checks using the `$verify-changes` skill to execute the full verification stack in order before considering the work complete.
 5.  Commit using Conventional Commits.
 6.  Push and open a pull request.

PATCH

echo "Patch applied successfully."

#!/usr/bin/env bash
set -euo pipefail

REPO=/workspace/openai-agents-js

cd "${REPO}"

# Create skill directory and scripts
mkdir -p .codex/skills/verify-changes/scripts

# Write SKILL.md
cat <<'SKILLEOF' > .codex/skills/verify-changes/SKILL.md
---
name: verify-changes
description: Run all mandatory verification steps for code changes in the OpenAI Agents JS monorepo.
---

# Verify Changes

## Overview

Ensure work is only marked complete after installing dependencies, building, linting, type checking, and tests pass. Use this skill whenever wrapping up a task, before opening a PR, or when asked to confirm that changes are ready to hand off.

## Quick start

1. Keep this skill at `./.codex/skills/verify-changes` so it loads automatically for the repository.
2. macOS/Linux: `bash .codex/skills/verify-changes/scripts/run.sh`.
3. Windows: `powershell -ExecutionPolicy Bypass -File .codex/skills/verify-changes/scripts/run.ps1`.
4. If any command fails, fix the issue, rerun the script, and report the failing output.
5. Confirm completion only when all commands succeed with no remaining issues.

## Manual workflow

- Run from the repository root in this order: `pnpm i`, `pnpm build`, `pnpm -r build-check`, `pnpm lint`, `pnpm test`.
- Do not skip steps; stop and fix issues immediately when a command fails.
- Re-run the full stack after applying fixes so the commands execute in the required order.

## Resources

### scripts/run.sh

- Executes the full verification sequence with fail-fast semantics.
- Prefer this entry point to ensure the commands always run in the correct order from the repo root.

### scripts/run.ps1

- Windows-friendly wrapper that runs the same verification sequence with fail-fast semantics.
- Use from PowerShell with execution policy bypass if required by your environment.
SKILLEOF

# Write run.sh
cat <<'SHEOF' > .codex/skills/verify-changes/scripts/run.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if command -v git >/dev/null 2>&1; then
  REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel 2>/dev/null || true)"
fi
REPO_ROOT="${REPO_ROOT:-$(cd "${SCRIPT_DIR}/../../../.." && pwd)}"

cd "${REPO_ROOT}"

echo "Running pnpm i..."
pnpm i

echo "Running pnpm build..."
pnpm build

echo "Running pnpm -r build-check..."
pnpm -r build-check

echo "Running pnpm lint..."
pnpm lint

echo "Running pnpm test..."
pnpm test

echo "verify-changes: all commands passed."
SHEOF

chmod +x .codex/skills/verify-changes/scripts/run.sh

# Write run.ps1
cat <<'PSEOF' > .codex/skills/verify-changes/scripts/run.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = $null

try {
    $repoRoot = (& git -C $scriptDir rev-parse --show-toplevel 2>$null)
} catch {
    $repoRoot = $null
}

if (-not $repoRoot) {
    $repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..\..")
}

Set-Location $repoRoot

function Invoke-PnpmStep {
    param(
        [Parameter(Mandatory = $true)][string[]]$Args
    )

    $commandText = "pnpm " + ($Args -join " ")
    Write-Host "Running $commandText..."
    & pnpm @Args

    if ($LASTEXITCODE -ne 0) {
        Write-Error "verify-changes: $commandText failed with exit code $LASTEXITCODE."
        exit $LASTEXITCODE
    }
}

Invoke-PnpmStep -Args @("i")
Invoke-PnpmStep -Args @("build")
Invoke-PnpmStep -Args @("-r", "build-check")
Invoke-PnpmStep -Args @("lint")
Invoke-PnpmStep -Args @("test")

Write-Host "verify-changes: all commands passed."
PSEOF

# Patch AGENTS.md — add Mandatory Skill Usage section and replace inline bash blocks
python3 <<'PYEOF'
import re

with open("AGENTS.md") as f:
    content = f.read()

# Insert "Mandatory Skill Usage" into ToC as first item
content = content.replace(
    "1.  [Overview](#overview)",
    "1.  [Mandatory Skill Usage](#mandatory-skill-usage)\n2.  [Overview](#overview)"
)

# Renumber ToC
for i in range(10, 1, -1):
    old = f"{i}. "
    new = f"{i+1}. "
    # Only replace ToC entries (after the "## Table of Contents" heading)
    parts = content.split("## Table of Contents")
    toc, rest = parts[0], parts[1]
    toc_end = rest.split("\n## ", 1)
    if len(toc_end) > 1:
        toc_body = toc_end[0]
        after_toc = "\n## " + toc_end[1]
    else:
        toc_body = rest
        after_toc = ""
    toc_body = toc_body.replace(f"\n{old}", f"\n{new}")
    content = toc + "## Table of Contents" + toc_body + after_toc

# Add "Mandatory Skill Usage" section after Table of Contents
content = content.replace(
    "## Overview\n",
    "## Mandatory Skill Usage\n\n"
    "Always load and use the `$verify-changes` skill immediately after any code change and before you consider the work complete. "
    "It executes the mandatory verification stack from the repository root; rerun the stack after fixing failures.\n\n"
    "## Overview\n"
)

# Update ExecPlans section to add backward compat note
content = content.replace(
    "When writing complex features or significant refactors, use an ExecPlan (as described in .agent/PLANS.md) from design to implementation.\n",
    "When writing complex features or significant refactors, use an ExecPlan (as described in .agent/PLANS.md) from design to implementation.\n"
    "Call out potential backward compatibility or public API risks in your plan and confirm the approach when changes could impact package consumers.\n"
)

# Update docs line to add translate note
content = content.replace(
    "- `docs/`: Documentation source; develop with `pnpm docs:dev` or build with `pnpm docs:build`.\n",
    "- `docs/`: Documentation source; develop with `pnpm docs:dev` or build with `pnpm docs:build`. "
    "Translated docs under `docs/src/content/docs/ja`, `docs/src/content/docs/ko`, and `docs/src/content/docs/zh` "
    "are generated via `pnpm docs:translate`; do not edit them manually.\n"
)

# Add skill reference after "Before submitting changes" paragraph
content = content.replace(
    "Before submitting changes, ensure all checks pass and augment tests when you touch code:\n\n",
    "Before submitting changes, ensure all checks pass and augment tests when you touch code:\n\n"
    "After any code modification, invoke the `$verify-changes` skill to run the required verification stack from the repository root. "
    "Rerun the full stack after fixes.\n\n"
)

# Replace Mandatory Local Run Order inline bash block
content = content.replace(
    "For every code change, run the full validation sequence locally:\n\n"
    "```bash\n"
    "pnpm lint && pnpm build && pnpm -r build-check && pnpm test\n"
    "```",
    "For every code change, run the full validation sequence locally via the `$verify-changes` skill; do not skip any step or change the order."
)

# Replace step 4 in Development Workflow inline bash block
content = content.replace(
    "4.  Run all checks (in this order):\n"
    "    ```bash\n"
    "    pnpm lint && pnpm build && pnpm -r build-check && pnpm test\n"
    "    ```",
    "4.  Run all checks using the `$verify-changes` skill to execute the full verification stack in order before considering the work complete."
)

with open("AGENTS.md", "w") as f:
    f.write(content)
PYEOF

# Idempotency check
grep -q "name: verify-changes" .codex/skills/verify-changes/SKILL.md && echo "Patch applied successfully"

#!/usr/bin/env bash
set -euo pipefail

REPO=/workspace/openai-agents-js
cd "$REPO"

# Idempotency: if the new skill file is already present with the renamed
# frontmatter, the gold has already been applied.
if grep -qF 'name: code-change-verification' .codex/skills/code-change-verification/SKILL.md 2>/dev/null; then
    echo "Gold already applied."
    exit 0
fi

# Remove the pre-rename skill directory entirely.
rm -rf .codex/skills/verify-changes

mkdir -p .codex/skills/code-change-verification/scripts
mkdir -p .codex/skills/openai-knowledge

# ---------------------------------------------------------------------------
# .codex/skills/code-change-verification/SKILL.md
# ---------------------------------------------------------------------------
cat > .codex/skills/code-change-verification/SKILL.md <<'SKILL_EOF'
---
name: code-change-verification
description: Run the mandatory verification stack when changes affect runtime code, tests, or build/test behavior in the OpenAI Agents JS monorepo.
---

# Code Change Verification

## Overview

Ensure work is only marked complete after installing dependencies, building, linting, type checking (including generated declarations), and tests pass. Use this skill when changes affect runtime code, tests, or build/test configuration.

## Quick start

1. Keep this skill at `./.codex/skills/code-change-verification` so it loads automatically for the repository.
2. macOS/Linux: `bash .codex/skills/code-change-verification/scripts/run.sh`.
3. Windows: `powershell -ExecutionPolicy Bypass -File .codex/skills/code-change-verification/scripts/run.ps1`.
4. If any command fails, fix the issue, rerun the script, and report the failing output.
5. Confirm completion only when all commands succeed with no remaining issues.

## Manual workflow

- Run from the repository root in this order: `pnpm i`, `pnpm build`, `pnpm -r build-check`, `pnpm -r -F "@openai/*" dist:check`, `pnpm lint`, `pnpm test`.
- Do not skip steps; stop and fix issues immediately when a command fails.
- Re-run the full stack after applying fixes so the commands execute in the required order.

## Resources

### scripts/run.sh

- Executes the full verification sequence (including declaration checks) with fail-fast semantics.
- Prefer this entry point to ensure the commands always run in the correct order from the repo root.

### scripts/run.ps1

- Windows-friendly wrapper that runs the same verification sequence with fail-fast semantics.
- Use from PowerShell with execution policy bypass if required by your environment.
SKILL_EOF

# ---------------------------------------------------------------------------
# .codex/skills/code-change-verification/scripts/run.sh
# ---------------------------------------------------------------------------
cat > .codex/skills/code-change-verification/scripts/run.sh <<'RUN_SH_EOF'
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

echo "Running pnpm -r -F \"@openai/*\" dist:check..."
pnpm -r -F "@openai/*" dist:check

echo "Running pnpm lint..."
pnpm lint

echo "Running pnpm test..."
pnpm test

echo "code-change-verification: all commands passed."
RUN_SH_EOF
chmod +x .codex/skills/code-change-verification/scripts/run.sh

# ---------------------------------------------------------------------------
# .codex/skills/code-change-verification/scripts/run.ps1
# ---------------------------------------------------------------------------
cat > .codex/skills/code-change-verification/scripts/run.ps1 <<'RUN_PS1_EOF'
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
        Write-Error "code-change-verification: $commandText failed with exit code $LASTEXITCODE."
        exit $LASTEXITCODE
    }
}

Invoke-PnpmStep -Args @("i")
Invoke-PnpmStep -Args @("build")
Invoke-PnpmStep -Args @("-r", "build-check")
Invoke-PnpmStep -Args @("-r", "-F", "@openai/*", "dist:check")
Invoke-PnpmStep -Args @("lint")
Invoke-PnpmStep -Args @("test")

Write-Host "code-change-verification: all commands passed."
RUN_PS1_EOF

# ---------------------------------------------------------------------------
# .codex/skills/openai-knowledge/SKILL.md
# ---------------------------------------------------------------------------
cat > .codex/skills/openai-knowledge/SKILL.md <<'KNOW_EOF'
---
name: openai-knowledge
description: Use when working with the OpenAI API (Responses API) or OpenAI platform features (tools, streaming, Realtime API, auth, models, rate limits, MCP) and you need authoritative, up-to-date documentation (schemas, examples, limits, edge cases). Prefer the OpenAI Developer Documentation MCP server tools when available; otherwise guide the user to enable `openaiDeveloperDocs`.
---

# OpenAI Knowledge

## Overview

Use the OpenAI Developer Documentation MCP server to search and fetch exact docs (markdown), then base your answer on that text instead of guessing.

## Workflow

### 1) Check whether the Docs MCP server is available

If the `mcp__openaiDeveloperDocs__*` tools are available, use them.

If you are unsure, run `codex mcp list` and check for `openaiDeveloperDocs`.

### 2) Use MCP tools to pull exact docs

- Search first, then fetch the specific page(s).
  - `mcp__openaiDeveloperDocs__search_openai_docs` → pick the best URL.
  - `mcp__openaiDeveloperDocs__fetch_openai_doc` → retrieve the exact markdown (optionally with an `anchor`).
- When you need endpoint schemas or parameters, use:
  - `mcp__openaiDeveloperDocs__get_openapi_spec`
  - `mcp__openaiDeveloperDocs__list_api_endpoints`

Base your answer on the fetched text and quote or paraphrase it precisely. Do not invent flags, field names, defaults, or limits.

### 3) If MCP is not configured, guide setup (do not change config unless asked)

Provide one of these setup options, then ask the user to restart the Codex session so the tools load:

- CLI:
  - `codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp`
- Config file (`~/.codex/config.toml`):
  - Add:
    ```toml
    [mcp_servers.openaiDeveloperDocs]
    url = "https://developers.openai.com/mcp"
    ```

Also point to: https://developers.openai.com/resources/docs-mcp#quickstart
KNOW_EOF

# ---------------------------------------------------------------------------
# AGENTS.md (overwrite with merged-state contents)
# ---------------------------------------------------------------------------
cat > AGENTS.md <<'AGENTS_EOF'
# Contributor Guide

This guide helps new contributors get started with the OpenAI Agents JS monorepo. It covers repo structure, how to test your work, available utilities, file locations, and guidelines for commits and PRs.

**Location:** `AGENTS.md` at the repository root.

## ExecPlans

When writing complex features or significant refactors, use an ExecPlan (as described in .agent/PLANS.md) from design to implementation.
Call out potential backward compatibility or public API risks in your plan and confirm the approach when changes could impact package consumers.

## Table of Contents

1.  [Mandatory Skill Usage](#mandatory-skill-usage)
2.  [Overview](#overview)
3.  [Repo Structure & Important Files](#repo-structure--important-files)
4.  [Testing & Automated Checks](#testing--automated-checks)
5.  [Repo-Specific Utilities](#repo-specific-utilities)
6.  [Style, Linting & Type Checking](#style-linting--type-checking)
7.  [Development Workflow](#development-workflow)
8.  [Pull Request & Commit Guidelines](#pull-request--commit-guidelines)
9.  [Review Process & What Reviewers Look For](#review-process--what-reviewers-look-for)
10. [Tips for Navigating the Repo](#tips-for-navigating-the-repo)
11. [Prerequisites](#prerequisites)

## Mandatory Skill Usage

### `$code-change-verification`

Run `$code-change-verification` before marking work complete when changes affect runtime code, tests, or build/test behavior.

Run it when you change:

- `packages/`, `examples/`, `helpers/`, `scripts/`, or `integration-tests/`
- Root build/test config such as `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsconfig*.json`, `eslint.config.*`, or `vitest*.ts`

You can skip `$code-change-verification` for docs-only or repo-meta changes (for example, `docs/`, `.codex/`, `README.md`, `AGENTS.md`, `.github/`), unless a user explicitly asks to run the full verification stack.

### `$openai-knowledge`

When working on OpenAI API or OpenAI platform integrations in this repo (Responses API, tools, streaming, Realtime API, auth, models, rate limits, MCP, Agents SDK/ChatGPT Apps SDK), use `$openai-knowledge` to pull authoritative docs via the OpenAI Developer Docs MCP server (and guide setup if it is not configured).

## Overview

The OpenAI Agents JS repository is a pnpm-managed monorepo that provides:

- `packages/agents`: A convenience bundle exporting core and OpenAI packages.
- `packages/agents-core`: Core abstractions and runtime for agent workflows.
- `packages/agents-openai`: OpenAI-specific bindings and implementations.
- `packages/agents-realtime`: Realtime bindings and implementations.
- `packages/agents-extensions`: Extensions for agent workflows.
- `docs`: Documentation site powered by Astro.
- `examples`: Sample projects demonstrating usage patterns.
- `scripts`: Automation scripts (`dev.mts`, `embedMeta.ts`).
- `helpers`: Shared utilities for testing and other internal use.

## Repo Structure & Important Files

- `packages/agents-core/`, `packages/agents-openai/`, `packages/agents-realtime/`, `packages/agents-extensions/`: Each has its own `package.json`, `src/`, `test/`, and build scripts.
- `docs/`: Documentation source; develop with `pnpm docs:dev` or build with `pnpm docs:build`. Translated docs under `docs/src/content/docs/ja`, `docs/src/content/docs/ko`, and `docs/src/content/docs/zh` are generated via `pnpm docs:translate`; do not edit them manually.
- `examples/`: Subdirectories (e.g. `basic`, `agent-patterns`) with their own `package.json` and start scripts.
- `scripts/dev.mts`: Runs concurrent build-watchers and the docs dev server (`pnpm dev`).
- `scripts/embedMeta.ts`: Generates `src/metadata.ts` for each package before build.
- `helpers/tests/`: Shared test utilities.
- `README.md`: High-level overview and installation instructions.
- `CONTRIBUTING.md`: Official contribution guidelines (this guide is complementary).
- `pnpm-workspace.yaml`: Defines workspace packages.
- `tsconfig.json`, `tsc-multi.json`: TypeScript configuration.
- `vitest.config.ts`: Test runner configuration.
- `eslint.config.mjs`: ESLint configuration.
- `package.json` (root): Common scripts (`build`, `test`, `lint`, `dev`, `docs:dev`, `examples:*`).

## Testing & Automated Checks

Before submitting changes, ensure all checks pass and augment tests when you touch code:

When `$code-change-verification` applies (see Mandatory Skill Usage), invoke it to run the required verification stack from the repository root. Rerun the full stack after fixes.

- Add or update unit tests for any code change unless it is truly infeasible; if something prevents adding tests, explain why in the PR.

### Unit Tests and Type Checking

- Check the compilation across all packages and examples:
  ```bash
  pnpm -r build-check
  ```
  NEVER USE `-w` or other watch modes.
- Run the full test suite:
  ```bash
  CI=1 pnpm test
  ```
- Tests are located under each package in `packages/<pkg>/test/`.
- The test script already sets `CI=1` to avoid watch mode.

### Integration Tests

- Not required for typical contributions. These tests rely on a local npm registry (Verdaccio) and other environment setup.
- To run locally only if needed:
  ```bash
  pnpm local-npm:start   # starts Verdaccio on :4873
  pnpm local-npm:publish # public pacakges to the local repo
  pnpm test:integration  # runs integration tests
  ```

See [this README](integration-tests/README.md) for details.

### Code Coverage

- Generate coverage report:
  ```bash
  pnpm test:coverage
  ```
- Reports output to `coverage/`.

### Linting & Formatting

- Run ESLint:
  ```bash
  pnpm lint
  ```
- Code style follows `eslint.config.mjs` and Prettier defaults.
- Comments must end with a period.

### Type Checking

- Ensure TypeScript errors are absent via build:
  ```bash
  pnpm build
  ```
- Build runs `tsx scripts/embedMeta.ts` (prebuild) and `tsc` for each package.

### Mandatory Local Run Order

When `$code-change-verification` applies (see Mandatory Skill Usage), run the full validation sequence locally via the `$code-change-verification` skill; do not skip any step or change the order.

### Pre-commit Hooks

- You can skip failing precommit hooks using `--no-verify` during commit.

## Repo-Specific Utilities

- `pnpm dev`:
  Runs concurrent watch builds for all packages and starts the docs dev server.
  ```bash
  pnpm dev
  ```
- Documentation site:
  ```bash
  pnpm docs:dev
  pnpm docs:build
  ```
- Examples:
  ```bash
  pnpm examples:basic
  pnpm examples:agents-as-tools
  pnpm examples:deterministic
  pnpm examples:tools-shell
  pnpm examples:tools-apply-patch
  # See root package.json "examples:*" scripts for full list
  ```
- Metadata embedding (prebuild):
  ```bash
  pnpm -F <package> build
  # runs embedMeta.ts automatically
  ```
- Workspace scoping (operate on a single package):
  ```bash
  pnpm -F agents-core build
  pnpm -F agents-openai test
  ```

## Style, Linting & Type Checking

- Follow ESLint rules (`eslint.config.mjs`), no unused imports, adhere to Prettier.
- Run `pnpm lint` and fix all errors locally.
- Use `pnpm build` to catch type errors.

## Prerequisites

- Node.js 22+ recommended.
- pnpm 10+ (`corepack enable` is recommended to manage versions).

## Development Workflow

1.  Sync with `main` (or default branch).
2.  Create a feature/fix branch with a descriptive name:
    ```bash
    git checkout -b feat/<short-description>
    ```
3.  Make changes and add/update unit tests in `packages/<pkg>/test` unless doing so is truly infeasible.
4.  When `$code-change-verification` applies (see Mandatory Skill Usage), run it to execute the full verification stack in order before considering the work complete.
5.  Commit using Conventional Commits.
6.  Push and open a pull request.

## Pull Request & Commit Guidelines

- Use **Conventional Commits**:
  - `feat`: new feature
  - `fix`: bug fix
  - `docs`: documentation only
  - `test`: adding or fixing tests
  - `chore`: build, CI, or tooling changes
  - `perf`: performance improvement
  - `refactor`: code changes without feature or fix
  - `build`: changes that affect the build system
  - `ci`: CI configuration
  - `style`: code style (formatting, missing semicolons, etc.)
  - `types`: type-related changes
  - `revert`: reverts a previous commit
- Commit message format:

  ```
  <type>(<scope>): <short summary>

  Optional longer description.
  ```

- Keep summary under 80 characters.
- If your change affects the public API, add a Changeset via:
  ```bash
  pnpm changeset
  ```

## Review Process & What Reviewers Look For

- ✅ All automated checks pass (build, tests, lint).
- ✅ Tests cover new behavior and edge cases.
- ✅ Code is readable and maintainable.
- ✅ Public APIs have doc comments.
- ✅ Examples updated if behavior changes.
- ✅ Documentation (in `docs/`) updated for user-facing changes.
- ✅ Commit history is clean and follows Conventional Commits.

## Tips for Navigating the Repo

- Use `pnpm -F <pkg>` to operate on a specific package.
- Study `vitest.config.ts` for test patterns (e.g., setup files, aliasing).
- Explore `scripts/embedMeta.ts` for metadata generation logic.
- Examples in `examples/` are fully functional apps—run them to understand usage.
- Docs in `docs/src/` use Astro and Starlight; authored content lives under `docs/src/content/docs/` and mirrors package APIs.
AGENTS_EOF

echo "Gold solution applied."

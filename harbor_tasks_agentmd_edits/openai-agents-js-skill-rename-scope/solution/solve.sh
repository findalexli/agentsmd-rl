#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openai-agents-js

# Idempotent: skip if already applied
if [ -d ".codex/skills/code-change-verification" ]; then
    echo "Patch already applied."
    exit 0
fi

# 1. Rename verify-changes → code-change-verification
git mv .codex/skills/verify-changes .codex/skills/code-change-verification

# 2. Update SKILL.md content
cat > .codex/skills/code-change-verification/SKILL.md <<'EOF'
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
EOF

# 3. Update run.sh message
sed -i 's/verify-changes: all commands passed/code-change-verification: all commands passed/' \
    .codex/skills/code-change-verification/scripts/run.sh

# 4. Update run.ps1 messages
sed -i 's/verify-changes:/code-change-verification:/g' \
    .codex/skills/code-change-verification/scripts/run.ps1

# 5. Create new openai-knowledge skill
mkdir -p .codex/skills/openai-knowledge
cat > .codex/skills/openai-knowledge/SKILL.md <<'EOF'
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
EOF

# 6. Update AGENTS.md - replace verify-changes references and add new sections
python3 <<'PYEOF'
with open("AGENTS.md", "r") as f:
    content = f.read()

# Replace the old Mandatory Skill Usage section
old_section = """## Mandatory Skill Usage

Always load and use the `$verify-changes` skill immediately after any code change and before you consider the work complete. It executes the mandatory verification stack from the repository root; rerun the stack after fixing failures."""

new_section = """## Mandatory Skill Usage

### `$code-change-verification`

Run `$code-change-verification` before marking work complete when changes affect runtime code, tests, or build/test behavior.

Run it when you change:

- `packages/`, `examples/`, `helpers/`, `scripts/`, or `integration-tests/`
- Root build/test config such as `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsconfig*.json`, `eslint.config.*`, or `vitest*.ts`

You can skip `$code-change-verification` for docs-only or repo-meta changes (for example, `docs/`, `.codex/`, `README.md`, `AGENTS.md`, `.github/`), unless a user explicitly asks to run the full verification stack.

### `$openai-knowledge`

When working on OpenAI API or OpenAI platform integrations in this repo (Responses API, tools, streaming, Realtime API, auth, models, rate limits, MCP, Agents SDK/ChatGPT Apps SDK), use `$openai-knowledge` to pull authoritative docs via the OpenAI Developer Docs MCP server (and guide setup if it is not configured)."""

content = content.replace(old_section, new_section)

# Replace remaining $verify-changes references
content = content.replace(
    "After any code modification, invoke the `$verify-changes` skill to run the required verification stack from the repository root. Rerun the full stack after fixes.",
    "When `$code-change-verification` applies (see Mandatory Skill Usage), invoke it to run the required verification stack from the repository root. Rerun the full stack after fixes."
)

content = content.replace(
    "For every code change, run the full validation sequence locally via the `$verify-changes` skill; do not skip any step or change the order.",
    "When `$code-change-verification` applies (see Mandatory Skill Usage), run the full validation sequence locally via the `$code-change-verification` skill; do not skip any step or change the order."
)

content = content.replace(
    "Run all checks using the `$verify-changes` skill to execute the full verification stack in order before considering the work complete.",
    "When `$code-change-verification` applies (see Mandatory Skill Usage), run it to execute the full verification stack in order before considering the work complete."
)

with open("AGENTS.md", "w") as f:
    f.write(content)
PYEOF

echo "Patch applied successfully."

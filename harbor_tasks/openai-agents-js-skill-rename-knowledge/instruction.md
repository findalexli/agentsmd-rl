# Task: Rename verify-changes skill, add openai-knowledge skill, update AGENTS.md

Update the agent configuration in this repository to rename the `verify-changes` skill, make its usage conditional, add a new `openai-knowledge` skill, and update AGENTS.md accordingly.

## Background

The repository currently has a skill at `.codex/skills/verify-changes/` that runs the full verification stack (install, build, lint, type-check, test). The AGENTS.md file in the repo root mandates running `$verify-changes` after every code change.

## What needs to change

### 1. Rename verify-changes to code-change-verification

The skill at `.codex/skills/verify-changes/` should be renamed to `.codex/skills/code-change-verification/`. This includes:
- Moving/renaming the directory and all files within it
- Updating the `name` field in the SKILL.md frontmatter to `code-change-verification`
- Updating the description to clarify the skill applies when changes affect runtime code, tests, or build/test behavior
- Updating the overview text so it no longer says to use the skill "whenever wrapping up a task, before opening a PR, or when asked to confirm that changes are ready to hand off" — instead it should say to use it "when changes affect runtime code, tests, or build/test configuration"
- Updating the quick-start paths from `verify-changes` to `code-change-verification`
- Updating the echo/Write-Host messages in `scripts/run.sh` and `scripts/run.ps1` to say `code-change-verification` instead of `verify-changes`

### 2. Make verification conditional

The `$code-change-verification` skill should be conditional — it should only be required for:
- Changes under `packages/`, `examples/`, `helpers/`, `scripts/`, or `integration-tests/`
- Changes to root build/test configuration files such as `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsconfig*.json`, `eslint.config.*`, or `vitest*.ts`

The skill can be **skipped** for docs-only or repo-meta changes, such as changes under `docs/`, `.codex/`, `README.md`, `AGENTS.md`, `.github/` — unless someone explicitly asks to run the full verification stack.

### 3. Add new openai-knowledge skill

Create a new skill at `.codex/skills/openai-knowledge/SKILL.md` with:
- Frontmatter `name: openai-knowledge`
- A description that says to use this skill when working with the OpenAI API (Responses API) or OpenAI platform features (tools, streaming, Realtime API, auth, models, rate limits, MCP) and the agent needs authoritative documentation
- Instructions to prefer the `openaiDeveloperDocs` MCP server tools when available, otherwise guide the user to enable it
- An Overview section explaining to use the OpenAI Developer Documentation MCP server to search and fetch exact docs
- A Workflow section with three steps:

**Step 1)** Check whether the Docs MCP server is available by looking for `mcp__openaiDeveloperDocs__*` tools, or running `codex mcp list` and checking for `openaiDeveloperDocs`.

**Step 2)** Use MCP tools to pull exact docs:
- `mcp__openaiDeveloperDocs__search_openai_docs` to search, then pick the best URL
- `mcp__openaiDeveloperDocs__fetch_openai_doc` to retrieve exact markdown (optionally with an `anchor`)
- `mcp__openaiDeveloperDocs__get_openapi_spec` and `mcp__openaiDeveloperDocs__list_api_endpoints` for endpoint schemas
- Base answers on fetched text and quote or paraphrase precisely; do not invent flags, field names, defaults, or limits

**Step 3)** If MCP is not configured, guide setup with either:
- CLI: `codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp`
- Config file (`~/.codex/config.toml`): add a `[mcp_servers.openaiDeveloperDocs]` section with `url = "https://developers.openai.com/mcp"`
- Point to: https://developers.openai.com/resources/docs-mcp#quickstart

### 4. Update AGENTS.md

Edit `AGENTS.md` so that:
- The "Mandatory Skill Usage" section is replaced with two subsections: one for `$code-change-verification` (a level-3 heading `### \`$code-change-verification\``) and one for `$openai-knowledge` (a level-3 heading `### \`$openai-knowledge\``)
- The `$code-change-verification` subsection describes the conditional trigger (runtime code, tests, build/test behavior), lists the directories and config files that trigger it, and states when it can be skipped (docs-only or repo-meta changes)
- The `$openai-knowledge` subsection says to use this skill for OpenAI API or platform integrations and to pull docs via the OpenAI Developer Docs MCP server
- Every remaining reference to `$verify-changes` in the file is updated to `$code-change-verification` and reworded to reference the conditional trigger ("When `$code-change-verification` applies (see Mandatory Skill Usage)"). There are several such references throughout the file — all must be updated.
- No stale references to `verify-changes` (the old name) remain in AGENTS.md

## Existing files to reference

Review the current content of `.codex/skills/verify-changes/SKILL.md` (the skill to rename) and `AGENTS.md` (the contributor guide) — they are both in the repository at the paths shown.

## Constraints

- Do not modify any files outside `.codex/skills/` and `AGENTS.md`
- Preserve the verification command sequence from the existing SKILL.md ("Manual workflow" section): `pnpm i`, `pnpm build`, `pnpm -r build-check`, `pnpm -r -F "@openai/*" dist:check`, `pnpm lint`, `pnpm test`
- Preserve the fail-fast instruction that says not to skip steps and to fix issues immediately
- The renamed scripts (`run.sh`, `run.ps1`) must remain functional — only update the string literals in echo/Write-Host/Write-Error messages
- All markdown files must follow existing repo conventions: frontmatter with `---` delimiters, level-2 `##` section headings, level-3 `###` sub-headings

## Code Style Requirements

- All comments and documentation text must end with a period
- Skill frontmatter must use the `name:` and `description:` fields

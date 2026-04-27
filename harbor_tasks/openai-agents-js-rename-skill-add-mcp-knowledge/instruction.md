# Refactor the Codex verification skill and add an OpenAI docs MCP skill

This monorepo (the OpenAI Agents JS SDK) ships Codex skill bundles under
`.codex/skills/` and a top-level `AGENTS.md` that tells Codex when to use
them. Right now `AGENTS.md` requires the `$verify-changes` skill to be run
after **any** code change — which is overbroad for docs-only or repo-meta
edits — and there is no documented entry point for using the OpenAI
Developer Documentation MCP server.

You will make three coordinated edits to fix this.

## 1. Rename the verification skill

The Codex skill currently shipped at `.codex/skills/verify-changes/` should
be moved to `.codex/skills/code-change-verification/`. The bundle keeps the
same shape: `SKILL.md` plus `scripts/run.sh` and `scripts/run.ps1`. After
the rename, the old `.codex/skills/verify-changes/` directory should no
longer exist, and the new bundle should be self-consistent (no leftover
`verify-changes` strings inside it).

While renaming, update the skill so it is conditional rather than
mandatory:

- The frontmatter `name:` field is `code-change-verification`.
- The frontmatter `description:` makes clear the skill should run the
  mandatory verification stack **when changes affect runtime code, tests,
  or build/test behavior** in this monorepo (rather than after every task).
- The `## Overview` and `## Quick start` sections refer to the new path
  and convey the same conditional scope.
- The bundled `scripts/run.sh` and `scripts/run.ps1` should print/log
  startup and error messages using the new identifier
  `code-change-verification:` (the prior `verify-changes:` prefix is no
  longer accurate). Do **not** change the underlying `pnpm i` / `pnpm
  build` / `pnpm -r build-check` / `pnpm -r -F "@openai/*" dist:check`
  / `pnpm lint` / `pnpm test` command sequence — only the identifier
  strings.

## 2. Add a new `openai-knowledge` skill

Create `.codex/skills/openai-knowledge/SKILL.md` describing how Codex
agents should pull authoritative OpenAI documentation when working on
OpenAI API or platform integrations.

Requirements:

- Frontmatter has `name: openai-knowledge` and a description that
  explains it is for working with the OpenAI API (Responses API) or
  OpenAI platform features — tools, streaming, Realtime API, auth,
  models, rate limits, MCP — and that it consults the OpenAI Developer
  Documentation MCP server.
- The body should tell the agent to prefer MCP tools whose names start
  with the `mcp__openaiDeveloperDocs__` prefix when they are available
  — at minimum a search helper (e.g. `search_openai_docs`) and a fetch
  helper (e.g. `fetch_openai_doc`) — and to base answers on the
  fetched markdown rather than guessing flags, field names, or defaults.
  It should also mention helpers for endpoint schemas
  (`get_openapi_spec`, `list_api_endpoints`).
- It should describe how to check whether the docs MCP server is
  configured (running `codex mcp list` and looking for
  `openaiDeveloperDocs`).
- For users without the MCP server configured, provide setup
  guidance: the CLI command
  `codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp`
  and an equivalent `[mcp_servers.openaiDeveloperDocs]` block in
  `~/.codex/config.toml` pointing at the same URL, plus a reminder to
  restart the Codex session and a pointer to the official quickstart at
  `https://developers.openai.com/resources/docs-mcp#quickstart`.

## 3. Update `AGENTS.md`

Re-work the **Mandatory Skill Usage** section so it has two clearly
labeled subsections, one per skill:

1. A `### \`$code-change-verification\`` subsection that:
   - Says the skill must be run before marking work complete **when
     changes affect runtime code, tests, or build/test behavior**.
   - Lists which directories/files trigger it (at minimum: `packages/`,
     `examples/`, `helpers/`, `scripts/`, `integration-tests/`, plus
     root build/test config such as `package.json`, `pnpm-lock.yaml`,
     `pnpm-workspace.yaml`, `tsconfig*.json`, `eslint.config.*`,
     `vitest*.ts`).
   - Names the categories that may skip the skill — docs-only and
     repo-meta — for example `docs/`, `.codex/`, `README.md`,
     `AGENTS.md`, `.github/`, unless the user explicitly requests the
     full verification stack.
2. A `### \`$openai-knowledge\`` subsection that says the skill must be
   used when working on OpenAI API or OpenAI platform integrations in
   this repo — Responses API, tools, streaming, Realtime API, auth,
   models, rate limits, MCP, Agents SDK / ChatGPT Apps SDK — to pull
   authoritative docs via the OpenAI Developer Docs MCP server (and
   guide setup if it is not configured).

Then update every other reference to `$verify-changes` further down in
`AGENTS.md` (the **Testing & Automated Checks** intro, **Mandatory Local
Run Order**, and the **Development Workflow** numbered list) so those
paragraphs:

- Use the new skill name `$code-change-verification`.
- Reflect that the skill is conditional ("When `$code-change-verification`
  applies (see Mandatory Skill Usage), …") rather than mandatory after
  *any* code change.

No `$verify-changes` references should remain anywhere in `AGENTS.md`
once you are done.

## Scope discipline

Sections of `AGENTS.md` unrelated to the skill rename — the Overview,
Repo Structure, Repo-Specific Utilities, Style/Linting, Prerequisites,
Conventional Commits guidelines, Review Process, Tips, etc. — should be
left intact. The `## Table of Contents` may stay as-is.

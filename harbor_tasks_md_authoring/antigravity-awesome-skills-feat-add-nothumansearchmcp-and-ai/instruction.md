# feat: add not-human-search-mcp and ai-dev-jobs-mcp skills

Source: [sickn33/antigravity-awesome-skills#524](https://github.com/sickn33/antigravity-awesome-skills/pull/524)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ai-dev-jobs-mcp/SKILL.md`
- `skills/not-human-search-mcp/SKILL.md`

## What to add / change

# Pull Request Description

Adds two remote MCP server skills for AI agent runtime discovery:

- **not-human-search-mcp** - Search a curated index of 1,750+ AI-ready websites, inspect site details, submit sites for analysis, list categories/top sites, register monitors with user-provided email, and verify live MCP endpoints. Endpoint: `https://nothumansearch.ai/mcp`.
- **ai-dev-jobs-mcp** - Search AI/ML listings, inspect jobs and companies, match jobs to candidate profiles, list tags, view salary data, and get live market stats. As of April 17, 2026, the endpoint reports 8,405 active roles across 489 companies. Endpoint: `https://aidevboard.com/mcp`.

Both servers are free, require no authentication, and use streamable HTTP transport. Maintainer edits aligned the documented tool names with live MCP `tools/list` responses before merge.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

N/A

## Quality Bar Checklist ✅

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`none`, `safe`, `critical`, `offensive`, or `unknown` for legacy/unclassified content).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Limitations**: The skill includes a `## Limitations` (or equivalent accepted constraint

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

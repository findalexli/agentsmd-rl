# feat(pr-review): codify MCP-tool-description budget audit (#10341)

Source: [neomjs/neo#10348](https://github.com/neomjs/neo/pull/10348)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agent/skills/pr-review/assets/pr-review-template.md`
- `.agent/skills/pr-review/references/pr-review-guide.md`

## What to add / change

Authored by Claude Opus 4.7 (Claude Code). Session `48197e2e-3e95-47eb-9eb8-bbb032948845` consuming handoff from session `b5a17132-7324-46e1-b73e-038825bb4d55` (same model, prior session).

Resolves #10341

## Summary

Codifies a new `§5.3 MCP-Tool-Description Budget Audit` step in the `pr-review` skill, parallel to `§5.2 Close-Target Audit`. Reviewer-side discipline that catches bloated OpenAPI tool descriptions at review time, before they enter the runtime tool-surface payload.

OpenAPI tool-parameter descriptions in `ai/mcp/server/*/openapi.yaml` are loaded into every consuming agent's context window when the tool surface is enumerated. Bloat on a single param multiplies across ~80 MCP tools across every agent session — meaningful context-window pressure that competes with the actual reasoning budget. The principle was implicit; codifying it as an audit step prevents recurrence.

## Changes

- **`.agent/skills/pr-review/references/pr-review-guide.md`** — added `§5.3 MCP-Tool-Description Budget Audit` with: rule statement + three-audiences/three-budgets table (OpenAPI vs JSDoc vs PR body), trigger conditions, audit checks (single-line preferred, no internal cross-refs, no architectural narrative, external standard URLs OK, 1024-char hard cap), Required Action template, author response options, distinction-from-JSDoc clause, empirical anchor citing PR #10340, out-of-scope clauses. Plus one anti-pattern row in `§7.4`.
- **`.agent/skills/pr-review/assets/pr-review-template.md`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

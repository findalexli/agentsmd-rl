# feat(zipai-optimizer): upgrade to v12.0 — MCP-aware rule, regression …

Source: [sickn33/antigravity-awesome-skills#549](https://github.com/sickn33/antigravity-awesome-skills/pull/549)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/zipai-optimizer/SKILL.md`

## What to add / change

## Summary

Upgrade `zipai-optimizer` from v11.0 to v12.0.

This PR improves the skill's token optimization rules with better coverage of MCP tool usage patterns, code review mode, regression safety, and input filtering edge cases.

### Changes

- **Rule 1 — Adaptive Verbosity:** added explicit Review mode with structured labels (`[ISSUE]`, `[SUGGESTION]`, `[NITPICK]`)
- **Rule 2 — Ambiguity-First:** added scope ambiguity case (file vs. project vs. repo)
- **Rule 3 — Intelligent Input Filtering:** added medium file tier (100–300 lines), MCP tool response handling, and `git blame` restriction
- **Rule 4 — Surgical Output:** added regression guard with `[RISK: untested path]` flag
- **Rule 5 — Context Pruning:** added `[DEPRECATED]` tag and multi-step progress anchors
- **Rule 6 — MCP-Aware Tool Usage:** new rule covering ID resolution, read-before-write, lazy pagination, SHA discipline, and error handling
- **Negative Constraints:** 3 new MCP-specific constraints added
- **Limitations:** added MCP Pagination Truncation limitation with `paginate:full` override

## Change Classification

- [x] Skill PR

## Quality Bar Checklist ✅

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: `risk: safe` — no offensive content, no network calls, no token-like strings.
- [x] **Triggers**: A

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

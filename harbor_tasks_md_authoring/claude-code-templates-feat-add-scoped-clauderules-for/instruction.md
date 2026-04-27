# feat: Add scoped .claude/rules for cli-tool, dashboard, and cloudflare

Source: [davila7/claude-code-templates#493](https://github.com/davila7/claude-code-templates/pull/493)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/cli-tool.md`
- `.claude/rules/cloudflare.md`
- `.claude/rules/dashboard.md`

## What to add / change

## Summary
- Add `.claude/rules/cli-tool.md` — scoped rules for CLI tool and component system (paths: `cli-tool/**`, `src/**`)
- Add `.claude/rules/dashboard.md` — scoped rules for Astro dashboard (paths: `dashboard/**`)
- Add `.claude/rules/cloudflare.md` — scoped rules for Cloudflare Workers (paths: `cloudflare-workers/**`)

These rules provide Claude Code with focused context per area of the codebase, reducing noise and improving suggestions when working in specific directories.

## Test plan
- [ ] Verify rules are picked up when editing files in `cli-tool/`, `src/`, `dashboard/`, and `cloudflare-workers/`
- [ ] Confirm frontmatter `paths` globs match intended directories

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Add path-scoped `.claude/rules` for the CLI, dashboard, and Cloudflare Workers so Claude Code loads focused guidance only in those areas. This reduces noise and improves suggestions during edits.

- CLI + components: Added `cli-tool.md` rules for `src/**` and `cli-tool/**`.
- Dashboard: Added `dashboard.md` rules for `dashboard/**`.
- Workers: Added `cloudflare.md` rules for `cloudflare-workers/**`.
- Areas affected: CLI, components, workers. No changes to website (`docs/`) or API.
- No new components; no `docs/components.json` regeneration needed. No new env vars or secrets.

<sup>Written for commit 71a78043c41a949666ca05524cc0d0356cee2900. Summary will update on new commits.</sup>

<!-- End of auto-generated description by

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

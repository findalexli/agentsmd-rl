# fix(skills): update ralph-wiggum references to ralph-loop in lfg/slfg

Source: [EveryInc/compound-engineering-plugin#324](https://github.com/EveryInc/compound-engineering-plugin/pull/324)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/lfg/SKILL.md`
- `plugins/compound-engineering/skills/slfg/SKILL.md`

## What to add / change

## Summary

Updates 3 stale `ralph-wiggum` references to `ralph-loop` in the `lfg` and `slfg` skills. The plugin was renamed from `ralph-wiggum` to `ralph-loop` (per [#306 comment](https://github.com/EveryInc/compound-engineering-plugin/issues/306#issuecomment-2737063839) by @iuriguilherme - renamed due to legal advice), but these skill files were not updated.

## Why this matters

Both `/lfg` and `/slfg` always skip Step 1 with "ralph-wiggum skill is not available - skipping" because they check for the old plugin name. Users must manually add "use ralph-loop instead of ralph-wiggum" to work around it ([#306](https://github.com/EveryInc/compound-engineering-plugin/issues/306)). Previously reported as [#154](https://github.com/EveryInc/compound-engineering-plugin/issues/154) (closed but not fixed).

## Changes

- `plugins/compound-engineering/skills/lfg/SKILL.md`: Updated skill availability check and invocation from `ralph-wiggum` to `ralph-loop` (lines 10, 36)
- `plugins/compound-engineering/skills/slfg/SKILL.md`: Same update (line 12)
- CHANGELOG.md historical entry left unchanged (it's a record of the rename)

## Testing

- Verified `ralph-wiggum` no longer appears in either skill file
- `bun run release:validate` passes (29 agents, 45 skills, 1 MCP server)

Fixes #306

This contribution was developed with AI assistance (Claude Code).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

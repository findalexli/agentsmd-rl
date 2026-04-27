# fix: quote frontend-design skill description

Source: [EveryInc/compound-engineering-plugin#353](https://github.com/EveryInc/compound-engineering-plugin/pull/353)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/frontend-design/SKILL.md`

## What to add / change

## Summary
- Quotes the `frontend-design` skill YAML description to prevent parsing issues with colons in the value
- Collapses multiline description into a single quoted line for clarity

Pulls out fix from #350

## Test plan
- [ ] Verify `bun run release:validate` passes
- [ ] Confirm skill description renders correctly in Claude Code

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

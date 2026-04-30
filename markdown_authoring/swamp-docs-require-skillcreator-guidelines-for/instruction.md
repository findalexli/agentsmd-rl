# docs: require skill-creator guidelines for swamp skill maintenance

Source: [systeminit/swamp#426](https://github.com/systeminit/swamp/pull/426)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

- Adds a note to CLAUDE.md requiring that all `swamp-*` skill changes follow
  the `skill-creator` skill guidelines

## Why

Without a shared standard, skills drift in structure and quality as different
authors (human or Claude) update them independently. This one-liner keeps the
`skill-creator` guidelines front of mind and ensures consistency across all
swamp skills.

## Test plan

- [ ] Verify CLAUDE.md renders correctly

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

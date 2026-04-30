# fix(skill): trim compound skill description under 250-char limit

Source: [backnotprop/plannotator#430](https://github.com/backnotprop/plannotator/pull/430)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `apps/skills/plannotator-compound/SKILL.md`

## What to add / change

## Summary
- Trims `plannotator-compound` skill description from 455 to 185 characters (under the new 250-char cap in Claude Code 2.1.86)
- Adds `disable-model-invocation: true` frontmatter to properly prevent auto-triggering, replacing contradictory prose that both listed trigger phrases and said "do not trigger automatically"
- Removes redundant trigger phrase list and invocation instructions from description

Closes #412

## Test plan
- [ ] Verify skill still appears in `/skills` listing without truncation
- [ ] Verify skill triggers correctly when user explicitly invokes it
- [ ] Verify skill does not auto-trigger on related prompts

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

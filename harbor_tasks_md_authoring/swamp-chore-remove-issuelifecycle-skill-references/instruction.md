# chore: Remove issue-lifecycle skill references as it's in giga-swamp now

Source: [systeminit/swamp#1196](https://github.com/systeminit/swamp/pull/1196)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/issue-lifecycle/SKILL.md`
- `.claude/skills/issue-lifecycle/references/adversarial-review.md`
- `.claude/skills/issue-lifecycle/references/implementation.md`
- `.claude/skills/issue-lifecycle/references/planning.md`
- `.claude/skills/issue-lifecycle/references/triage.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

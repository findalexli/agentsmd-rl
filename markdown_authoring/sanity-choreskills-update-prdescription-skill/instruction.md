# chore(skills): update pr-description skill

Source: [sanity-io/sanity#12697](https://github.com/sanity-io/sanity/pull/12697)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/pr-description/SKILL.md`

## What to add / change

### Description

The `pr-description` skill was producing descriptions that over-explained _what_ changed (restating diff content) and under-explained _why_ and the alternatives that were considered and rejected. Restructures the guidance around a clear hierarchy: heavy on _why_, cover _why not_, light on _how_, minimal _what_ — with a length test ("if a sentence is deducible from the diff in 10 seconds, cut it").

### What to review

- `.agents/skills/pr-description/SKILL.md` — the only changed file

### Testing

Skill prompts aren't automatable. Validated by using the updated skill to write this PR's description.

### Notes for release

N/A – Internal tooling only

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

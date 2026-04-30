# opencode/skills/*

Source: [coreos/butane#692](https://github.com/coreos/butane/pull/692)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.opencode/skills/add-sugar/SKILL.md`
- `.opencode/skills/remove-feature/SKILL.md`
- `.opencode/skills/stabilize-spec/SKILL.md`

## What to add / change

Lets start adding opencode skills for common tasks, to enable ease of use on common tasks.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

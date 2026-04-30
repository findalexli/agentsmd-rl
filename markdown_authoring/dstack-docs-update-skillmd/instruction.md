# [Docs] Update SKILL.md

Source: [dstackai/dstack#3547](https://github.com/dstackai/dstack/pull/3547)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/dstack/SKILL.md`

## What to add / change

* Corrected a typo in the configuration type help command.
* Enhanced descriptions for `dstack offer` command, including details on max offers and grouping options.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

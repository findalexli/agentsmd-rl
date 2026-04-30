# Add AGENTS.md to rust directory

Source: [KittyCAD/modeling-app#10007](https://github.com/KittyCAD/modeling-app/pull/10007)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `rust/AGENTS.md`

## What to add / change

This basically summarizes the readme files we already have in a more concise way that's designed for development.

Please, make suggestions!

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

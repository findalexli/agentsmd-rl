# chore: update AGENTS.md

Source: [ocaml/dune#14180](https://github.com/ocaml/dune/pull/14180)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

I can't tell if the agent even reads this file, but hopefully this can't hurt.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

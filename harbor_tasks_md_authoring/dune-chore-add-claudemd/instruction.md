# chore: add CLAUDE.md

Source: [ocaml/dune#12529](https://github.com/ocaml/dune/pull/12529)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Basic CLAUDE.md. Improvements are welcome, this is just a starting point.

Signed-off-by: Rudi Grinberg <me@rgrinberg.com>

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

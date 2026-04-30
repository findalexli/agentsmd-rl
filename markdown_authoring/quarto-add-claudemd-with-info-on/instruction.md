# Add `claude.md` with info on the repo structure, to help Claude know where things are

Source: [quarto-dev/quarto#840](https://github.com/quarto-dev/quarto/pull/840)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `claude.md`

## What to add / change

If I ever use Claude Code in this repo, I have to spend time telling Claude where things are or have it spend tokens finding out itself. Maybe we can try this out? On some initial exploration it seems pretty helpful.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

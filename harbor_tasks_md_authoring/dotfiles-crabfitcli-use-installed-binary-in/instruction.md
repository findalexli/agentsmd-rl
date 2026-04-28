# crabfit-cli: use installed binary in SKILL.md

Source: [Mic92/dotfiles#4512](https://github.com/Mic92/dotfiles/pull/4512)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `pkgs/crabfit-cli/SKILL.md`

## What to add / change

The tool is now available in $PATH as crabfit-cli, so update the
documentation to use the installed command instead of invoking
python3 directly on the source file.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

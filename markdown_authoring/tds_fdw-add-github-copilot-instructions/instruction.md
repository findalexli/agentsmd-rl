# Add GitHub Copilot Instructions

Source: [tds-fdw/tds_fdw#406](https://github.com/tds-fdw/tds_fdw/pull/406)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This file is used by GitHub Copilot integration in IDEs like VS Code.

https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

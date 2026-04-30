# add CLAUDE.md with version management automation

Source: [IITC-CE/ingress-intel-total-conversion#859](https://github.com/IITC-CE/ingress-intel-total-conversion/pull/859)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Added documentation for automated version updates of IITC core and plugins. Includes commands for checking changes since last release, updating version numbers based on change type (patch/minor), and synchronizing mobile app version.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

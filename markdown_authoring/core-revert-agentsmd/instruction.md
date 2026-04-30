# Revert "AGENTS.md"

Source: [home-assistant/core#153777](https://github.com/home-assistant/core/pull/153777)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `CLAUDE.md`

## What to add / change

Reverts home-assistant/core#153680

I think we should revert that one, because on double checking, copilot supports the AGENTS.md only for the coding agent, but not for code review 
Ref: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
@Shulyaka FYI

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

# doc: rename chain CLAUDE.md to AGENTS.md

Source: [near/nearcore#15172](https://github.com/near/nearcore/pull/15172)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `chain/chain/AGENTS.md`

## What to add / change

From CONTRIBUTING.md Coding Agents section:
> Individual modules or subprojects may provide their own `AGENTS.md` files with
module-specific instructions.

Followup to #15168.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

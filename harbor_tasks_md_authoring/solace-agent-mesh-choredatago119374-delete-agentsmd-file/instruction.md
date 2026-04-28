# chore(DATAGO-119374): Delete AGENTS.md file

Source: [SolaceLabs/solace-agent-mesh#684](https://github.com/SolaceLabs/solace-agent-mesh/pull/684)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

**Problem:**
Agents.md file will change the coding experience of internal developers. 

**Changes:**
Delete the AGENTS.md to revert the repository status to the past. This is the corresponding [PR](https://github.com/SolaceLabs/solace-agent-mesh/pull/681).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

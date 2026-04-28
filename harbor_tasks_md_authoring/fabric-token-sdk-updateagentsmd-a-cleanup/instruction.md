# update(AGENTS.md): a cleanup

Source: [hyperledger-labs/fabric-token-sdk#1548](https://github.com/hyperledger-labs/fabric-token-sdk/pull/1548)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

This PR updates AGENTS.md to allow claude to load it more easily and to make it easier for the agent to follow the instructions

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

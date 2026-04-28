# added 'private keys' to the list of secrets

Source: [matank001/cursor-security-rules#4](https://github.com/matank001/cursor-security-rules/pull/4)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `secure-dev-node.mdc`
- `secure-dev-python.mdc`
- `secure-development-principles.mdc`
- `secure-mcp-usage.mdc`

## What to add / change

added 'private keys'  as the potential list of secret-types

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

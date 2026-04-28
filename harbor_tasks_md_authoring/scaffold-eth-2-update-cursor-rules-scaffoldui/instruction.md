# Update cursor rules (scaffold-ui)

Source: [scaffold-eth/scaffold-eth-2#1195](https://github.com/scaffold-eth/scaffold-eth-2/pull/1195)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/scaffold-eth.mdc`

## What to add / change

Let's update the cursor rules so it knows about the new scaffold-ui packages.

Do we need to add something else?

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

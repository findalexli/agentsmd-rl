# Add soroban-test integration testing instructions to copilot instructions

Source: [stellar/stellar-cli#2264](https://github.com/stellar/stellar-cli/pull/2264)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

### What
  Add documentation for running soroban-test integration tests using cargo test with the it feature flag. Include guidance that all new commands and command changes require corresponding test updates in soroban-test.

  ### Why
  The soroban-test integration tests contain the bulk of CLI command tests, but instructions for running them were missing from the copilot instructions.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

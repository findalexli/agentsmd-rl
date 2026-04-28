# Add copilot instructions

Source: [systemd/systemd#39224](https://github.com/systemd/systemd/pull/39224)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This was generated using copilot itself with Claude Sonnet 4.5 as the backing model.

The idea is to test this out on some PRs to see whether copilot can provide useful PR reviews. The idea is that it'll be able to take care of the low hanging fruit like coding style issues and such. Once we get some feedback on how it performs, we can make more changes to this document to get it to behave better (assuming we decide to keep using it at all).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

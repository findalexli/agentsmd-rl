# Add symlinked CLAUDE.md file

Source: [microsoft/vscode#291967](https://github.com/microsoft/vscode/pull/291967)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`

## What to add / change

Works well on macOS and should work on Windows:
> * Windows compatibility: On Windows, symlinks require Developer Mode enabled or admin privileges. Without these, git clone will create a regular file containing the symlink path as text.

<!-- Thank you for submitting a Pull Request. Please:
* Read our Pull Request guidelines:
  https://github.com/microsoft/vscode/wiki/How-to-Contribute#pull-requests
* Associate an issue with the Pull Request.
* Ensure that the code is up-to-date with the `main` branch.
* Include a description of the proposed changes and how to test them.
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

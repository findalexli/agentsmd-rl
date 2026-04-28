# TW-2089: Agents.md setup

Source: [madfish-solutions/templewallet-extension#1492](https://github.com/madfish-solutions/templewallet-extension/pull/1492)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

https://madfish.atlassian.net/jira/software/projects/TW/boards/4?selectedIssue=TW-2089

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

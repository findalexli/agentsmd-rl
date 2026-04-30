# Setup CLAUDE.md

Source: [workleap/wl-dotnet-codingstandards#144](https://github.com/workleap/wl-dotnet-codingstandards/pull/144)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Jira issue link: [FENG-1896](https://workleap.atlassian.net/browse/FENG-1896)



[FENG-1896]: https://workleap.atlassian.net/browse/FENG-1896?atlOrigin=eyJpIjoiNWRkNTljNzYxNjVmNDY3MDlhMDU5Y2ZhYzA5YTRkZjUiLCJwIjoiZ2l0aHViLWNvbS1KU1cifQ

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

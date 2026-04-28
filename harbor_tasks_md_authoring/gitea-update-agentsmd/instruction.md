# Update AGENTS.md

Source: [go-gitea/gitea#37420](https://github.com/go-gitea/gitea/pull/37420)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

`make test-sqlite#TestName` was much too slow, suggest `go test`. Also added a similar instruction for js tests.

---
This PR was written with the help of Claude Opus 4.7

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

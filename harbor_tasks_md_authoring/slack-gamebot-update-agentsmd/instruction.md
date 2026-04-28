# Update AGENTS.md

Source: [dblock/slack-gamebot#250](https://github.com/dblock/slack-gamebot/pull/250)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Ports instructions from discord-strava:
- Add **Starting Work** section: checkout master, git pull, delete merged branches before creating a new branch.
- Never push directly to master — always work on a branch and open a PR.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

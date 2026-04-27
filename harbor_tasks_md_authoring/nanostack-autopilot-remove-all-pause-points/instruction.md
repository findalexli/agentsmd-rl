# Autopilot: remove all pause points for uninterrupted sprints

Source: [garagon/nanostack#81](https://github.com/garagon/nanostack/pull/81)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plan/SKILL.md`
- `ship/SKILL.md`
- `think/SKILL.md`

## What to add / change

## Summary
Three skills paused for user input during autopilot, breaking the autonomous flow:

- **/think**: Asked diagnostic questions ("is this for learning or production?"). Now defaults to Builder mode in autopilot, skips questions, goes straight to scope recommendation.
- **/nano**: Waited for plan approval. Now auto-approves in autopilot and proceeds immediately.
- **/ship**: Asked "How do you want to see it?" Now skips the question in autopilot, goes to compound + sprint summary.

## The autopilot contract
After the user approves the /think brief, everything runs without stopping. Only blocking issues or critical vulnerabilities pause the sprint.

## Context
Found during live test with `--dangerously-skip-permissions`. The sprint ran to completion but /think stopped to ask if the user wanted to use an existing library vs build from scratch. In autopilot, the agent should make that call.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

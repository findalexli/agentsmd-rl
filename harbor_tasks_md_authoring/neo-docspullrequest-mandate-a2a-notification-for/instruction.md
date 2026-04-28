# docs(pull-request): mandate A2A notification for core swarm (#10405)

Source: [neomjs/neo#10406](https://github.com/neomjs/neo/pull/10406)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agent/skills/pull-request/references/pull-request-workflow.md`

## What to add / change

Resolves #10405

Updates the pull-request workflow documentation to mandate that core swarm members (Gemini, Claude) MUST send an A2A notification via `add_message` to peers immediately after opening a PR inside the `neomjs/neo` repository. This reduces duplicated work and ticket collision.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

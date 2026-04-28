# Update CLAUDE.md workflow and review process

Source: [levu304/claude-code-boilerplate#1](https://github.com/levu304/claude-code-boilerplate/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Add "No Code, No Problem" slogan to AI Agent Workflow section
- Replace fixed 3-review process with score-based approval system
- PRs now require average team review score of 9.5+/10 to merge
- Add iterative review cycle: fix all issues, repeat until score met
- Update implementation process table with new review steps
- Update workflow diagram with score-based decision flow
- Add review scoring criteria and focus areas by agent

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

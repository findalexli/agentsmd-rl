# feat(skills): Add triage-reviews skill for PR review verification

Source: [stickerdaniel/linkedin-mcp-server#276](https://github.com/stickerdaniel/linkedin-mcp-server/pull/276)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/triage-reviews/SKILL.md`

## What to add / change

Cross-agent skill at .agents/skills/triage-reviews/.
Fetches PR comments, verifies findings against real code/docs,
fixes valid issues, and pushes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

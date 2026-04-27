# docs(tend): deflect niche feature requests to aliases

Source: [max-sixty/worktrunk#2129](https://github.com/max-sixty/worktrunk/pull/2129)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/running-tend/SKILL.md`

## What to add / change

Sharpens the existing tend-triage guidance so the agent has a clear decision criterion: niche requests (small subset of users, single reporter's workflow) should be answered with a tested alias rather than implemented as a native flag.

Adds concrete edge cases for testing (branch already exists, dirty worktree, missing remote) and links to tips & patterns alongside the aliases docs.

> _This was written by Claude Code on behalf of Maximilian_

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

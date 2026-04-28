# [Chore] Add CLAUDE.md

Source: [DataRecce/recce#894](https://github.com/DataRecce/recce/pull/894)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

<!--  Thanks for sending a pull request!  Here are some check items for you: -->

**PR checklist**

- [x] Ensure you have added or ran the appropriate tests for your PR.
- [x] DCO signed

**What type of PR is this?**
Chore

**What this PR does / why we need it**:
Follow the practices in https://docs.claude.com/en/docs/claude-code/memory
Devlopers can have common knowledge about recce and can have personal preference at `~/.claude/recce.md`

**Which issue(s) this PR fixes**:

**Special notes for your reviewer**:

**Does this PR introduce a user-facing change?**:
<!--
If no, just write "NONE" in the release-note block below.
If yes, a release note is required:
Enter your extended release note in the block below. If the PR requires additional action from users switching to the new release, include the string "action required".
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

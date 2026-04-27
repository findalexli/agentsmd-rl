# docs: add AGENTS.md with issue-filing guidelines

Source: [JetBrains/teamcity-cli#235](https://github.com/JetBrains/teamcity-cli/pull/235)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Adds `AGENTS.md` with instructions for AI agents to check issue templates before filing, follow template structure, and verify labels exist
- Includes specific guidance for eval task issues (`eval_task.yml`)

## Context
Filed from session where agent skipped `.github/ISSUE_TEMPLATE/` and tried to create a freeform issue on a repo with `blank_issues_enabled: false`. See #234 for the eval issue that triggered this.

## Test plan
- [x] Verify `AGENTS.md` is picked up by Claude Code / Copilot / Gemini CLI in new sessions
- [x] File a test eval issue and confirm the agent follows the template

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

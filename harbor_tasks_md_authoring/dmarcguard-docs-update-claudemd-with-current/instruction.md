# docs: update CLAUDE.md with current codebase state

Source: [dmarcguardhq/dmarcguard#79](https://github.com/dmarcguardhq/dmarcguard/pull/79)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Update Go version to 1.25.4 (exact version from go.mod)
- Add SettingsModal.vue component and stores directory to structure
- Document all OAuth-related CLI flags for MCP server
- Add new deployment options: Zeabur, Render, Northflank
- Add `update-zeabur-template` Just command
- Document frontend state management (theme.js, settings.js)
- Add Settings Modal feature to frontend features list

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

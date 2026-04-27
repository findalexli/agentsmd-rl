# Updated the skills to remind users to resume the Claude Code sessions and eliminate the extra confirmation

Source: [microsoft/Dataverse-skills#16](https://github.com/microsoft/Dataverse-skills/pull/16)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/plugins/dataverse/skills/init/SKILL.md`
- `.github/plugins/dataverse/skills/mcp-configure/SKILL.md`
- `.github/plugins/dataverse/skills/overview/SKILL.md`
- `.github/plugins/dataverse/skills/setup/SKILL.md`

## What to add / change

- Updating multiple skills to remind users to use `claude --continue` when restarting to pick up PATH or MCP config changes
- Removing the `claude mcp add` command confirmation and moving the `npx` proxy test into troubleshooting
- Improved wording around cross-references from `dataverse-mcp-config` to `dataverse-init` to make agents default to initialization more reliably.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

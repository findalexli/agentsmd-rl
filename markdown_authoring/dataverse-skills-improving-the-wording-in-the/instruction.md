# Improving the wording in the init skill to ensure the environment URL is confirmed and no steps are skipped

Source: [microsoft/Dataverse-skills#5](https://github.com/microsoft/Dataverse-skills/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/plugins/dataverse/skills/init/SKILL.md`
- `.github/plugins/dataverse/skills/mcp-configure/SKILL.md`

## What to add / change

This PR modifies the wording to prevent two issues:
- The environment URL being assumed based on `pac auth list` without confirmation (also reported by others during validation)
- The MCP configuration step being skipped

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

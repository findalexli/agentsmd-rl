# Improve init UX, auth prompts, and MCP client whitelisting for non-developer users

Source: [microsoft/Dataverse-skills#15](https://github.com/microsoft/Dataverse-skills/pull/15)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/plugins/dataverse/skills/init/SKILL.md`
- `.github/plugins/dataverse/skills/mcp-configure/SKILL.md`
- `.github/plugins/dataverse/skills/overview/SKILL.md`

## What to add / change

Three changes to reduce friction for non-developer users:

1. Overview: auto-invoke init when workspace is missing instead of stopping and asking the user to run it manually
2. Init: present authentication as an explicit two-option choice (interactive login vs service principal) with clear descriptions of what each option means and when to use it
3. MCP Configure: replace admin-only consent URL (step 7) with step-by-step PPAC portal instructions (Environment > Settings > Features > MCP Server > Add client) as the primary path. Admin consent URL kept as secondary option for users with Azure AD admin permissions. Troubleshooting updated to match.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

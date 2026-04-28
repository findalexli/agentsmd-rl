# Add claude skills for profile authoring

Source: [ComplianceAsCode/content#14430](https://github.com/ComplianceAsCode/content/pull/14430)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`
- `.claude/skills/find-rule/SKILL.md`
- `.claude/skills/manage-profile/SKILL.md`

## What to add / change

- **Add a CLAUDE.md file**
- **Add CLAUDE command for find-rule**
- **Add CLAUDE command for manage-profile**

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

# Improve Claude Skills front matter

Source: [ComplianceAsCode/content#14657](https://github.com/ComplianceAsCode/content/pull/14657)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/find-rule/SKILL.md`
- `.claude/skills/manage-profile/SKILL.md`

## What to add / change

Add name and description to find-rule and manage-profile skills because the description field is used by Claude to decide when to use a skill, and it also determines how it's presented in the skill listing.

Remove `disable-model-invocation: true` from find-rule because find-rule is a pure search/lookup skill with zero side effects: it only reads files and presents results. Setting `disable-model-invocation: true` prevents Claude from automatically using it when a user asks something like "are there any rules for SSH timeout?" This defeats the purpose. It should be auto-invocable.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

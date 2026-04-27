# Update migration skill description to mention Call Control

Source: [team-telnyx/ai#23](https://github.com/team-telnyx/ai/pull/23)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `telnyx-twilio-migration/skills/telnyx-twilio-migration/SKILL.md`

## What to add / change

## Summary
- Adds "Call Control API guidance" to the migration skill's frontmatter description
- The skill already covers Call Control (comparison table, decision guide, code example) but the description didn't mention it, making it undiscoverable

## Test plan
- [ ] Verify frontmatter YAML parses correctly
- [ ] Confirm description renders properly in marketplace

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

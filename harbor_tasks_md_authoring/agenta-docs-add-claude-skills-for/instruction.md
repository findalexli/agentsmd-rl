# docs: add Claude skills for changelog and announcements

Source: [Agenta-AI/agenta#3427](https://github.com/Agenta-AI/agenta/pull/3427)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-announcement/SKILL.md`
- `.claude/skills/create-changelog-announcement/SKILL.md`
- `.claude/skills/write-social-announcement/SKILL.md`

## What to add / change

## Summary
- Add Claude/OpenCode skills for creating changelog announcements
- Add skill for writing social media announcements (LinkedIn, Twitter, Slack)
- Add skill for adding sidebar banner announcements

These skills provide structured guidelines for AI assistants to help create consistent changelog entries, social posts, and in-app announcements following project standards.

**Skills included:**
- `add-announcement` - Adding sidebar banner cards
- `create-changelog-announcement` - Full changelog workflow
- `write-social-announcement` - Social media writing guidelines

All files reviewed and verified to contain no personal information.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

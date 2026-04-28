# feat(core): add explicit-configuration skill

Source: [TheBushidoCollective/han#82](https://github.com/TheBushidoCollective/han/pull/82)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/core/skills/explicit-configuration/SKILL.md`

## What to add / change

## Summary
- Add new `explicit-configuration` skill to `plugins/core/skills/`
- Guides agents to prefer explicit configuration over framework defaults to prevent environment-dependent failures
- Includes examples for database connections, API calls, framework config, and security settings

## Test plan
- [ ] Verify `SKILL.md` frontmatter parses correctly (name, user-invocable, description, allowed-tools)
- [ ] Confirm skill appears in core plugin skill listing
- [ ] Validate markdown renders properly

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

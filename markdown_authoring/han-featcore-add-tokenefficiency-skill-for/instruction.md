# feat(core): add token-efficiency skill for minimizing consumption

Source: [TheBushidoCollective/han#83](https://github.com/TheBushidoCollective/han/pull/83)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/core/skills/token-efficiency/SKILL.md`

## What to add / change

## Summary

- Adds a new `token-efficiency` core skill that teaches agents to minimize token consumption through efficient tool usage patterns
- Covers file operations (prefer Edit over Write), search operations (prefer Glob/Grep over Bash), and context management (lead with answers, skip filler)
- Includes an anti-patterns table contrasting wasteful vs efficient approaches

## Test plan

- [ ] Verify SKILL.md frontmatter parses correctly (name, user-invocable, description, allowed-tools)
- [ ] Confirm skill is discoverable via han's plugin/skill loading mechanism
- [ ] Review guidelines align with Claude Code tool behavior

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

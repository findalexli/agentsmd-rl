# feat(core): add silent-execution skill

Source: [TheBushidoCollective/han#81](https://github.com/TheBushidoCollective/han/pull/81)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/core/skills/silent-execution/SKILL.md`

## What to add / change

## Summary
- Adds a new `silent-execution` skill to `plugins/core/skills/` that instructs agents to batch independent tool calls and avoid narration between sequential operations
- Non-user-invocable skill aimed at reducing token waste (~1,000-2,000 tokens saved per session)

## Test plan
- [ ] Verify SKILL.md frontmatter parses correctly (name, user-invocable, description, allowed-tools)
- [ ] Confirm skill is discovered by the plugin loader

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

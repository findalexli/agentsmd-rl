# feat: add agent skill for proper MCP database querying

Source: [bytebase/dbhub#265](https://github.com/bytebase/dbhub/pull/265)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/dbhub/SKILL.md`

## What to add / change

## Summary
- Adds a new agent skill at `/skills/dbhub/SKILL.md` that guides AI agents on the correct workflow for querying databases via DBHub's MCP tools
- Teaches the **explore-then-query** pattern: discover schemas → find tables → inspect structure → write precise SQL
- Covers progressive disclosure with `detail_level`, multi-database `source_id` routing, error recovery, and common anti-patterns
- Installable via `npx skills add bytebase/dbhub`

Closes #264

## Test plan
- [ ] Verify SKILL.md renders correctly on GitHub
- [ ] Test skill installation with `npx skills add bytebase/dbhub`
- [ ] Validate that agents follow the explore-then-query workflow when the skill is active

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

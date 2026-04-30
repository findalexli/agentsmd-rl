# Add ClickHouse best practices skill reference to AGENTS.md

Source: [514-labs/moosestack#3582](https://github.com/514-labs/moosestack/pull/3582)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Adds a "ClickHouse Best Practices" section to `AGENTS.md` pointing AI agents to the `moosestack-clickhouse-best-practices` skill (28 rules covering schema design, query optimization, and insert strategy)
- Includes install command (`npx skills add 514-labs/agent-skills`) for users who don't have the skill yet
- Fixes missing newline at end of file

## Test plan
- [x] Verified skill directory path (`~/.claude/skills/moosestack-clickhouse-best-practices/`) matches installed skill name
- [x] Verified `npx skills add 514-labs/agent-skills` works and finds the skill
- [x] Confirmed 28 rule files exist in `rules/` directory
- [x] Confirmed no duplicate content with other checked-in files (CLAUDE.md is generated from AGENTS.md)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Documentation-only change (plus newline fix) with no runtime or behavioral impact.
> 
> **Overview**
> Updates `AGENTS.md` to add a new **ClickHouse Best Practices** section that directs contributors/agents to the external `moosestack-clickhouse-best-practices` skill (schema design, query optimization, insert strategy) and includes the install command.
> 
> Also fixes the missing newline at EOF in `AGENTS.md`.
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit 5abb6ce66f57c7695c6c85de97bf166fe7e3fd23. This will update automatically on new commits. Configure [here](https://cursor.com/dashboa

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

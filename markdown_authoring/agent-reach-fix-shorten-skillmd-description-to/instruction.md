# fix: shorten SKILL.md description to stay under 1024-char limit

Source: [Panniantong/Agent-Reach#166](https://github.com/Panniantong/Agent-Reach/pull/166)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `agent_reach/skill/SKILL.md`

## What to add / change

Fixes #163

## Problem

The `description` field in `agent_reach/skill/SKILL.md` was **1204 characters**, exceeding the **1024-character maximum** enforced by Codex and other MCP clients. This caused:

```
invalid description: exceeds maximum length of 1024 characters
```

…preventing the skill from loading entirely.

## Fix

Shortened the description from 1204 → **661 characters** (well within the 1024 limit) while preserving all essential information:

| What | Before | After |
|------|--------|-------|
| Platform list | With Chinese aliases in parens | Names only (aliases in triggers) |
| Star count | "7500+ GitHub stars" | Removed (changes frequently) |
| Use-when rules | 5 numbered items | 1 concise sentence |
| Trigger keywords | 34 triggers | 23 most distinctive triggers |

All key trigger keywords for platform matching are preserved. The removed duplicates (e.g. both `搜推特` and `search twitter`) were redundant — agents match on any trigger, so keeping one form is sufficient.

## Testing

Verified the YAML frontmatter parses correctly and the new description is 661 chars.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

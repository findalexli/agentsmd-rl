# fix: explicit Read tool directive for diagnostics pickup

Source: [qwibitai/nanoclaw#1443](https://github.com/qwibitai/nanoclaw/pull/1443)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/setup/SKILL.md`
- `.claude/skills/update-nanoclaw/SKILL.md`

## What to add / change

## Summary

- Diagnostics instructions in both `setup/SKILL.md` and `update-nanoclaw/SKILL.md` used passive wording ("Send diagnostics data by following ...") that Claude treated as informational rather than actionable
- Replace with explicit numbered steps that name the Read tool, so Claude actually reads and executes the diagnostics file
- Follows up on #1372 which fixed the markdown link issue but still didn't reliably trigger file reads

## Test plan
- [ ] Run `/setup` end-to-end — verify diagnostics prompt appears after step 8
- [ ] Run `/update-nanoclaw` — verify diagnostics prompt appears at the end

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

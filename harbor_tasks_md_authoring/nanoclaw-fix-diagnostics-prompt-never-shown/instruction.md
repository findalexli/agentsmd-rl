# fix: diagnostics prompt never shown to user

Source: [qwibitai/nanoclaw#1372](https://github.com/qwibitai/nanoclaw/pull/1372)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/setup/SKILL.md`
- `.claude/skills/setup/diagnostics.md`
- `.claude/skills/update-nanoclaw/SKILL.md`
- `.claude/skills/update-nanoclaw/diagnostics.md`

## What to add / change

## Summary

- Diagnostics section used a markdown link (`[diagnostics.md](diagnostics.md)`) that Claude never resolved — the prompt was silently skipped every time
- Replace with explicit Read tool directive as a numbered step (setup `## 9.`) and mandatory final step (update-nanoclaw)
- Update opt-out instructions in both `diagnostics.md` files to reference the renamed section headings

## Test plan
- [ ] Run `/setup` end-to-end — verify diagnostics prompt appears after step 8
- [ ] Run `/update-nanoclaw` — verify diagnostics prompt appears at the end
- [ ] Choose "Never ask again" — verify both SKILL.md sections and diagnostics.md files are updated correctly

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

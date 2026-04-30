# fix(codex-review): SKILL.md priority read + script paths

Source: [artwist-polyakov/polyakov-claude-skills#28](https://github.com/artwist-polyakov/polyakov-claude-skills/pull/28)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/codex-review/skills/codex-review/SKILL.md`

## What to add / change

## Summary

- Frontmatter: добавлена инструкция читать SKILL.md до любых других шагов
- Добавлена секция «Расположение скриптов» — Claude не находил скрипты при установке через marketplace

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

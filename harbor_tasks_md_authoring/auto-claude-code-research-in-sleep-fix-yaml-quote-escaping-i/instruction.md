# Fix YAML quote escaping in Claude review skills

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#58](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/58)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/skills-codex-claude-review/auto-paper-improvement-loop/SKILL.md`
- `skills/skills-codex-claude-review/paper-figure/SKILL.md`
- `skills/skills-codex-claude-review/paper-plan/SKILL.md`
- `skills/skills-codex-claude-review/paper-write/SKILL.md`

## What to add / change

Fix over-escaped quotes in YAML front matter descriptions for Claude review skills.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

# 📚 Add `AGENTS.md` and Claude Code skills

Source: [aiidateam/aiida-core#7265](https://github.com/aiidateam/aiida-core/pull/7265)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/adding-a-cli-command/SKILL.md`
- `.claude/skills/adding-dependencies/SKILL.md`
- `.claude/skills/architecture-overview/SKILL.md`
- `.claude/skills/commit-conventions/SKILL.md`
- `.claude/skills/debugging-processes/SKILL.md`
- `.claude/skills/deprecating-api/SKILL.md`
- `.claude/skills/linting-and-ci/SKILL.md`
- `.claude/skills/running-tests/SKILL.md`
- `.claude/skills/writing-and-building-docs/SKILL.md`
- `.claude/skills/writing-tests/SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Rendered view here:
https://github.com/GeigerJ2/aiida-core/blob/docs/agents_contributing/AGENTS.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

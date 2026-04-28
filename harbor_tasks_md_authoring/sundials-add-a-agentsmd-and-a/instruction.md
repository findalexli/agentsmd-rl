# Add a AGENTS.md and a couple of SKILLS

Source: [llnl/sundials#893](https://github.com/llnl/sundials/pull/893)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/building/SKILL.md`
- `.agents/skills/new-module/SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Add an [AGENTS.md](https://agents.md/) and some [SKILLS](https://agentskills.io/home) for us to get started with!

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

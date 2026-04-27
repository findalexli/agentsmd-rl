# Add A-Evolve agentic evolution skill -- https://github.com/A-EVO-Lab/a-evolve

Source: [aiming-lab/AutoResearchClaw#187](https://github.com/aiming-lab/AutoResearchClaw/pull/187)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/a-evolve/SKILL.md`

## What to add / change

Adds a new skill under .claude/skills/a-evolve/ that implements the Solve -> Observe -> Evolve -> Gate -> Reload methodology from A-Evolve for iterative agent self-improvement.

Ref: https://github.com/A-EVO-Lab/a-evolve

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

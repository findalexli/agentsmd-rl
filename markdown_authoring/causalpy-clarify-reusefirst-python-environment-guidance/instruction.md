# Clarify reuse-first Python environment guidance

Source: [pymc-labs/CausalPy#808](https://github.com/pymc-labs/CausalPy/pull/808)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/python-environment/SKILL.md`
- `AGENTS.md`

## What to add / change

## Summary
- clarify in `AGENTS.md` and the `python-environment` skill that agents should reuse an existing `CausalPy` environment and only create or update one when needed
- explain when the project environment is actually required versus when plain `python` is enough for simple local inspection helpers
- add a `run -p <full-prefix>` fallback plus guidance for editable installs in git worktrees and reuse on persistent remote machines

This reduces unnecessary setup work and token/time overhead while preserving the existing guidance for tasks that truly need the project environment.

## Test plan
- [x] `mamba run -p "/Users/benjamv/mambaforge/envs/CausalPy" prek run --all-files`


Made with [Cursor](https://cursor.com)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

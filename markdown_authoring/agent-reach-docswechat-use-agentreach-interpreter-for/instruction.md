# docs(wechat): use agent-reach interpreter for miku_ai search example

Source: [Panniantong/Agent-Reach#188](https://github.com/Panniantong/Agent-Reach/pull/188)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `agent_reach/skill/SKILL.md`

## What to add / change

## Problem

Fixes #187

`miku_ai` is installed **inside the agent-reach Python environment** (via `pipx inject` or `pip install` into the same venv). When users install agent-reach via pipx (the recommended method in `docs/install.md`), the system `python3` is a different interpreter — it cannot import `miku_ai`, causing `ModuleNotFoundError`.

The SKILL.md search example used bare `python3 -c ...`, which silently breaks for pipx users.

## Fix

Detect the correct interpreter at runtime:
```bash
AGENT_REACH_PYTHON=$(python3 -c "import agent_reach, sys; print(sys.executable)" 2>/dev/null || echo python3)
```

This resolves correctly for all install methods:
- **pipx**: resolves to `~/.local/share/pipx/venvs/agent-reach/bin/python`
- **venv**: resolves to the venv's python
- **plain pip / system install**: falls back to `python3` (same as before)

No hardcoded paths; no new dependencies.

## Verification

- `python3 -m pytest tests/ -x -q` → **49 passed**
- Diff: 1 file, 7 lines changed (SKILL.md only)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

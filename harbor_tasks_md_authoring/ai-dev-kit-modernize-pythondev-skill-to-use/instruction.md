# Modernize python-dev skill to use uv exclusively

Source: [databricks-solutions/ai-dev-kit#134](https://github.com/databricks-solutions/ai-dev-kit/pull/134)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/python-dev/SKILL.md`

## What to add / change

## Summary

- **Rewrote Environment Management section** in the `python-dev` skill to use `uv` exclusively — removed all references to `pip`, `python3 -m venv`, `conda`, `requirements.txt`, and manual venv activation
- **Added dedicated Code Quality subsections** for Ruff (linting & formatting) and Pyright (type checking) with runnable command examples
- **Updated Best Practices summary** to reflect the modern toolchain (`uv`, Ruff, Pyright)

## Motivation

The skill previously contained conflicting guidance — it mentioned `uv` alongside `venv`, `pip install`, and `requirements.txt`, leaving ambiguity about which workflow to follow. This aligns the skill with the Astral.sh toolchain (`uv` + `ruff`) that the project already uses.

## What changed

| Section | Before | After |
|---------|--------|-------|
| Dependency Management | `uv` or `venv`, check `.venv`, activate | `uv` exclusively, `pyproject.toml` only |
| Environment Setup | Shell script with `venv`/`pip`/`uv pip` | `uv sync` / `uv run` / `uv add` examples |
| Script Execution | "Activate venv, use `python3`" | `uv run` — no activation needed |
| Code Style | Single Ruff bullet | Full Ruff section (check, fix, format) |
| Type Checking | Not mentioned | Pyright section |
| Best Practices #6 | "uv or venv, activate before use" | `uv` exclusively, Ruff, Pyright |

## What was removed

- `pip install -r requirements.txt`
- `python3 -m venv .venv` / `source .venv/bin/activate`
- `uv pip install` (deprecated subcommand pat

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

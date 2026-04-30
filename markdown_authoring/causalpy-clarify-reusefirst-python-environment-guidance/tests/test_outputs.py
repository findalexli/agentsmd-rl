"""Behavioral checks for causalpy-clarify-reusefirst-python-environment-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/causalpy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/python-environment/SKILL.md')
    assert 'Git worktrees do not require a fresh env per agent session. Prefer reusing an existing env to save time. The main caveat is that this repo uses editable installs, so one shared env can point at whiche' in text, "expected to find: " + 'Git worktrees do not require a fresh env per agent session. Prefer reusing an existing env to save time. The main caveat is that this repo uses editable installs, so one shared env can point at whiche'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/python-environment/SKILL.md')
    assert 'description: Detect, configure, and use a conda-compatible tool. Use before tasks that need the project environment, such as importing project code, running tests, building docs, or invoking repo tool' in text, "expected to find: " + 'description: Detect, configure, and use a conda-compatible tool. Use before tasks that need the project environment, such as importing project code, running tests, building docs, or invoking repo tool'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/python-environment/SKILL.md')
    assert 'Run `make setup` after creating or updating the env. Also rerun it when using a different git worktree if that env has not been installed against the current checkout yet.' in text, "expected to find: " + 'Run `make setup` after creating or updating the env. Also rerun it when using a different git worktree if that env has not been installed against the current checkout yet.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Use `mamba`, `micromamba`, or `conda` (in that preference order) to manage the `CausalPy` environment. Reuse an existing `CausalPy` env whenever possible; do not create or update an env unless the tas' in text, "expected to find: " + 'Use `mamba`, `micromamba`, or `conda` (in that preference order) to manage the `CausalPy` environment. Reuse an existing `CausalPy` env whenever possible; do not create or update an env unless the tas'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- In git worktrees, prefer reusing an existing env. Because the repo uses editable installs, rerun `make setup` in the current worktree only when that checkout has not been installed into the env yet ' in text, "expected to find: " + '- In git worktrees, prefer reusing an existing env. Because the repo uses editable installs, rerun `make setup` in the current worktree only when that checkout has not been installed into the env yet '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- If `$CONDA_EXE run -n CausalPy ...` fails because the named env cannot be resolved, inspect `$CONDA_EXE env list` and retry with `$CONDA_EXE run -p <full-prefix> <command>`.' in text, "expected to find: " + '- If `$CONDA_EXE run -n CausalPy ...` fails because the named env cannot be resolved, inspect `$CONDA_EXE env list` and retry with `$CONDA_EXE run -p <full-prefix> <command>`.'[:80]


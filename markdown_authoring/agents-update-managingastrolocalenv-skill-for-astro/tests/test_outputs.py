"""Behavioral checks for agents-update-managingastrolocalenv-skill-for-astro (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/managing-astro-local-env/SKILL.md')
    assert 'description: Manage local Airflow environment with Astro CLI (Docker and standalone modes). Use when the user wants to start, stop, or restart Airflow, view logs, query the Airflow API, troubleshoot, ' in text, "expected to find: " + 'description: Manage local Airflow environment with Astro CLI (Docker and standalone modes). Use when the user wants to start, stop, or restart Airflow, view logs, query the Airflow API, troubleshoot, '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/managing-astro-local-env/SKILL.md')
    assert '> If you used `--standalone` on start instead of setting the config, pass `--standalone` on every subsequent command too (stop, kill, restart, bash, run, logs, etc.).' in text, "expected to find: " + '> If you used `--standalone` on start instead of setting the config, pass `--standalone` on every subsequent command too (stop, kill, restart, bash, run, logs, etc.).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/managing-astro-local-env/SKILL.md')
    assert 'Two modes: **Docker** (default, uses containers) and **Standalone** (Docker-free, uses a local venv — requires Airflow 3 + `uv`).' in text, "expected to find: " + 'Two modes: **Docker** (default, uses containers) and **Standalone** (Docker-free, uses a local venv — requires Airflow 3 + `uv`).'[:80]


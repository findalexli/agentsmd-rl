"""Behavioral checks for agents-feat-add-astro-cli-local (markdown_authoring task).

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
    text = _read('shared-skills/astro-local-env/SKILL.md')
    assert 'description: Manage local Airflow environment with Astro CLI. Use when the user wants to start, stop, or restart Airflow, view logs, troubleshoot containers, or fix environment issues. For project set' in text, "expected to find: " + 'description: Manage local Airflow environment with Astro CLI. Use when the user wants to start, stop, or restart Airflow, view logs, troubleshoot containers, or fix environment issues. For project set'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('shared-skills/astro-local-env/SKILL.md')
    assert '> **When Airflow is running**, use MCP tools from **dag-authoring** and **dag-testing** skills.' in text, "expected to find: " + '> **When Airflow is running**, use MCP tools from **dag-authoring** and **dag-testing** skills.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('shared-skills/astro-local-env/SKILL.md')
    assert 'This skill helps you manage your local Airflow environment using the Astro CLI.' in text, "expected to find: " + 'This skill helps you manage your local Airflow environment using the Astro CLI.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('shared-skills/astro-project-setup/SKILL.md')
    assert 'description: Initialize and configure Astro/Airflow projects. Use when the user wants to create a new project, set up dependencies, configure connections/variables, or understand project structure. Fo' in text, "expected to find: " + 'description: Initialize and configure Astro/Airflow projects. Use when the user wants to create a new project, set up dependencies, configure connections/variables, or understand project structure. Fo'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('shared-skills/astro-project-setup/SKILL.md')
    assert 'This skill helps you initialize and configure Airflow projects using the Astro CLI.' in text, "expected to find: " + 'This skill helps you initialize and configure Airflow projects using the Astro CLI.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('shared-skills/astro-project-setup/SKILL.md')
    assert 'RUN pip install --extra-index-url https://pypi.example.com/simple my-package' in text, "expected to find: " + 'RUN pip install --extra-index-url https://pypi.example.com/simple my-package'[:80]


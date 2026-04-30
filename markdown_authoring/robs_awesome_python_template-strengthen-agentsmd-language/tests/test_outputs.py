"""Behavioral checks for robs_awesome_python_template-strengthen-agentsmd-language (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/robs-awesome-python-template")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('{{cookiecutter.__package_slug}}/AGENTS.md')
    assert 'Before beginning any task, make sure you review the documentation (`docs/dev/` and `README.md`), the existing tests to understand the project, and the task runner (Makefile) to understand what dev too' in text, "expected to find: " + 'Before beginning any task, make sure you review the documentation (`docs/dev/` and `README.md`), the existing tests to understand the project, and the task runner (Makefile) to understand what dev too'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('{{cookiecutter.__package_slug}}/AGENTS.md')
    assert 'You must always follow the best practices outlined in this document. If there is a valid reason why you cannot follow one of these practices, you must inform the user and document the reasons.' in text, "expected to find: " + 'You must always follow the best practices outlined in this document. If there is a valid reason why you cannot follow one of these practices, you must inform the user and document the reasons.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('{{cookiecutter.__package_slug}}/AGENTS.md')
    assert '* Use different Pydantic models for inputs and outputs (i.e., creating a `Post` must require a `PostCreate` and return a `PostRead` model, not reuse the same model).' in text, "expected to find: " + '* Use different Pydantic models for inputs and outputs (i.e., creating a `Post` must require a `PostCreate` and return a `PostRead` model, not reuse the same model).'[:80]


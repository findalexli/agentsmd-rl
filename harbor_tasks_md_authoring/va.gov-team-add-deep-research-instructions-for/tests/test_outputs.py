"""Behavioral checks for va.gov-team-add-deep-research-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/va.gov-team")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The summary files (`.github/copilot-summaries/*.md`) provide **metadata** about research studies (who, when, methodology). For questions that require **analyzing actual research content and findings**' in text, "expected to find: " + 'The summary files (`.github/copilot-summaries/*.md`) provide **metadata** about research studies (who, when, methodology). For questions that require **analyzing actual research content and findings**'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| "What pain points did we discover in research?" | **Deep research** | Need to read findings from files |' in text, "expected to find: " + '| "What pain points did we discover in research?" | **Deep research** | Need to read findings from files |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| "How did research influence design decisions?" | **Deep research** | Tracing impact through documents |' in text, "expected to find: " + '| "How did research influence design decisions?" | **Deep research** | Tracing impact through documents |'[:80]


"""Behavioral checks for ml-for-beginners-add-agentsmd-file-to-provide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ml-for-beginners")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is **Machine Learning for Beginners**, a comprehensive 12-week, 26-lesson curriculum covering classic machine learning concepts using Python (primarily with Scikit-learn) and R. The repository is' in text, "expected to find: " + 'This is **Machine Learning for Beginners**, a comprehensive 12-week, 26-lesson curriculum covering classic machine learning concepts using Python (primarily with Scikit-learn) and R. The repository is'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Microsoft Learn Collection**: [ML for Beginners modules](https://learn.microsoft.com/en-us/collections/qrqzamz1nn2wx3?WT.mc_id=academic-77952-bethanycheum)' in text, "expected to find: " + '- **Microsoft Learn Collection**: [ML for Beginners modules](https://learn.microsoft.com/en-us/collections/qrqzamz1nn2wx3?WT.mc_id=academic-77952-bethanycheum)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Educational Content**: 26 lessons covering introduction to ML, regression, classification, clustering, NLP, time series, and reinforcement learning' in text, "expected to find: " + '- **Educational Content**: 26 lessons covering introduction to ML, regression, classification, clustering, NLP, time series, and reinforcement learning'[:80]


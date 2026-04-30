"""Behavioral checks for prefect-docs-document-pagination-limit-pitfall (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prefect")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/e2e/AGENTS.md')
    assert 'When testing pagination, set a small enough `limit` in the URL so the next-page button stays enabled even after filters are applied. A large limit (e.g., `limit=5`) against a filtered data set that re' in text, "expected to find: " + 'When testing pagination, set a small enough `limit` in the URL so the next-page button stays enabled even after filters are applied. A large limit (e.g., `limit=5`) against a filtered data set that re'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/e2e/AGENTS.md')
    assert 'Always assert `toBeEnabled()` rather than conditionally checking — the conditional silently turns a pagination test into a no-op when setup conditions change.' in text, "expected to find: " + 'Always assert `toBeEnabled()` rather than conditionally checking — the conditional silently turns a pagination test into a no-op when setup conditions change.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/e2e/AGENTS.md')
    assert '// ❌ Fragile - filtering may reduce results to ≤ limit, so next-page is never available' in text, "expected to find: " + '// ❌ Fragile - filtering may reduce results to ≤ limit, so next-page is never available'[:80]


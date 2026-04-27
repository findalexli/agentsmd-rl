"""Behavioral checks for awesome-cursorrules-add-convex-cursorrules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-cursorrules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/convex-cursorrules-prompt-file/.cursorrules')
    assert "Convex's built-in primitives are pretty low level! They're just functions. What about authentication frameworks? What about object-relational mappings? Do you need to wait until Convex ships some in-b" in text, "expected to find: " + "Convex's built-in primitives are pretty low level! They're just functions. What about authentication frameworks? What about object-relational mappings? Do you need to wait until Convex ships some in-b"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/convex-cursorrules-prompt-file/.cursorrules')
    assert 'Database indexes with range expressions allow you to write efficient database queries that only scan a small number of documents in the table. Pagination allows you to quickly display incremental list' in text, "expected to find: " + 'Database indexes with range expressions allow you to write efficient database queries that only scan a small number of documents in the table. Pagination allows you to quickly display incremental list'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/convex-cursorrules-prompt-file/.cursorrules')
    assert "While actions could work with thousands of records and call dozens of APIs, it's normally best to do smaller batches of work and/or to perform individual transformations with outside services. Then re" in text, "expected to find: " + "While actions could work with thousands of records and call dozens of APIs, it's normally best to do smaller batches of work and/or to perform individual transformations with outside services. Then re"[:80]


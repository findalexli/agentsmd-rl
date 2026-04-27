"""Behavioral checks for compound-engineering-plugin-fixdocumentreview-show-contextua (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/document-review/SKILL.md')
    assert 'Offer these two options. Use the document type from Phase 1 to set the "Review complete" description:' in text, "expected to find: " + 'Offer these two options. Use the document type from Phase 1 to set the "Review complete" description:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/document-review/SKILL.md')
    assert '1. **Refine again** -- Address the findings above, then re-review' in text, "expected to find: " + '1. **Refine again** -- Address the findings above, then re-review'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/document-review/SKILL.md')
    assert '2. **Review complete** -- description based on document type:' in text, "expected to find: " + '2. **Review complete** -- description based on document type:'[:80]


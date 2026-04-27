"""Behavioral checks for antigravity-awesome-skills-featodooedi-implement-idempotency (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/odoo-edi-connector/SKILL.md')
    assert 'partner_name = transaction.get_segment(\'N1\')[2] if transaction.get_segment(\'N1\') else "Unknown"' in text, "expected to find: " + 'partner_name = transaction.get_segment(\'N1\')[2] if transaction.get_segment(\'N1\') else "Unknown"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/odoo-edi-connector/SKILL.md')
    assert 'print(f"Error: Partner \'{partner_name}\' not found. Skipping transaction.")' in text, "expected to find: " + 'print(f"Error: Partner \'{partner_name}\' not found. Skipping transaction.")'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/odoo-edi-connector/SKILL.md')
    assert "existing = models.execute_kw(db, uid, pwd, 'sale.order', 'search', [" in text, "expected to find: " + "existing = models.execute_kw(db, uid, pwd, 'sale.order', 'search', ["[:80]


"""Behavioral checks for antigravity-awesome-skills-secodoo-mitigate-hardcoded-creden (markdown_authoring task).

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
    text = _read('skills/odoo-woocommerce-bridge/SKILL.md')
    assert 'odoo_url = os.getenv("ODOO_URL", "https://myodoo.example.com")' in text, "expected to find: " + 'odoo_url = os.getenv("ODOO_URL", "https://myodoo.example.com")'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/odoo-woocommerce-bridge/SKILL.md')
    assert 'url=os.getenv("WC_URL", "https://mystore.com"),' in text, "expected to find: " + 'url=os.getenv("WC_URL", "https://mystore.com"),'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/odoo-woocommerce-bridge/SKILL.md')
    assert 'consumer_secret=os.getenv("WC_SECRET"),' in text, "expected to find: " + 'consumer_secret=os.getenv("WC_SECRET"),'[:80]


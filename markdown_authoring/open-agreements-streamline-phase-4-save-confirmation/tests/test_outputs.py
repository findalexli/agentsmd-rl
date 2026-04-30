"""Behavioral checks for open-agreements-streamline-phase-4-save-confirmation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/open-agreements")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/delaware-franchise-tax/SKILL.md')
    assert 'The portal downloads the receipt as `Ecorp_Confirmation_<ServiceRequestNumber>.pdf` to the default Downloads folder. Move it to a durable location:' in text, "expected to find: " + 'The portal downloads the receipt as `Ecorp_Confirmation_<ServiceRequestNumber>.pdf` to the default Downloads folder. Move it to a durable location:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/delaware-franchise-tax/SKILL.md')
    assert 'The downloaded confirmation PDF **is** the filing record — no need to create a separate one.' in text, "expected to find: " + 'The downloaded confirmation PDF **is** the filing record — no need to create a separate one.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/delaware-franchise-tax/SKILL.md')
    assert '- Keep the original filename — it contains the Service Request Number for future reference' in text, "expected to find: " + '- Keep the original filename — it contains the Service Request Number for future reference'[:80]


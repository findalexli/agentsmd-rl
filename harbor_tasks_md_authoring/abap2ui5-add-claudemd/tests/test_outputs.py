"""Behavioral checks for abap2ui5-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/abap2ui5")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Layer 0 (`src/00/`)** — Self-contained utility libraries. AJSON handles all JSON work; S-RTTI provides runtime type reflection. These have no dependency on the framework itself. The `noIssues` fla' in text, "expected to find: " + '- **Layer 0 (`src/00/`)** — Self-contained utility libraries. AJSON handles all JSON work; S-RTTI provides runtime type reflection. These have no dependency on the framework itself. The `noIssues` fla'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. **Multi-environment compatibility matters.** Code must work across NW 7.02, standard ABAP, and ABAP Cloud. The `downport` rule in abaplint enforces this. Avoid syntax that only exists in newer ABAP' in text, "expected to find: " + '3. **Multi-environment compatibility matters.** Code must work across NW 7.02, standard ABAP, and ABAP Cloud. The `downport` rule in abaplint enforces this. Avoid syntax that only exists in newer ABAP'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'abap2UI5 is a framework for building SAP UI5 applications purely in ABAP — no JavaScript, OData, or RAP required. It supports all ABAP releases from NW 7.02 to ABAP Cloud, running in both on-premise a' in text, "expected to find: " + 'abap2UI5 is a framework for building SAP UI5 applications purely in ABAP — no JavaScript, OData, or RAP required. It supports all ABAP releases from NW 7.02 to ABAP Cloud, running in both on-premise a'[:80]


"""Behavioral checks for qtpass-docs-restore-qtpass-patterns-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/qtpass")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'In ConfigDialog, use `getProfiles()`/`setProfiles()` to preserve non-selected profile settings:' in text, "expected to find: " + 'In ConfigDialog, use `getProfiles()`/`setProfiles()` to preserve non-selected profile settings:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'QString profileName = ui->profileTable->item(selected.first()->row(), 0)->text();' in text, "expected to find: " + 'QString profileName = ui->profileTable->item(selected.first()->row(), 0)->text();'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'setProfiles(QtPassSettings::getProfiles(), QtPassSettings::getProfile());' in text, "expected to find: " + 'setProfiles(QtPassSettings::getProfiles(), QtPassSettings::getProfile());'[:80]


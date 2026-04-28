"""Behavioral checks for kopia-choreinfra-tweak-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kopia")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '11. **Trust these instructions** - These instructions have been validated by running all commands. Only search for additional information if something fails or if these instructions are incomplete or ' in text, "expected to find: " + '11. **Trust these instructions** - These instructions have been validated by running all commands. Only search for additional information if something fails or if these instructions are incomplete or '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '4. **Provider tests require environment:** Provider tests need KOPIA_PROVIDER_TEST=true and storage credentials.' in text, "expected to find: " + '4. **Provider tests require environment:** Provider tests need KOPIA_PROVIDER_TEST=true and storage credentials.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Note: Linting is **NOT** run on linux/arm64 or linux/arm platforms to avoid issues.' in text, "expected to find: " + 'Note: Linting is **NOT** run on linux/arm64 or linux/arm platforms to avoid issues.'[:80]


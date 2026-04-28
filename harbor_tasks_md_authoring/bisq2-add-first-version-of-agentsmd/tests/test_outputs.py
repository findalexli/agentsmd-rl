"""Behavioral checks for bisq2-add-first-version-of-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bisq2")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- For i18n strings, only update the base file in `i18n/src/main/resources/<name>.properties` and do not edit `..._<lang>.properties` files directly.' in text, "expected to find: " + '- For i18n strings, only update the base file in `i18n/src/main/resources/<name>.properties` and do not edit `..._<lang>.properties` files directly.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run desktop app: `./apps/desktop/desktop-app/build/install/desktop-app/bin/desktop-app`' in text, "expected to find: " + '- Run desktop app: `./apps/desktop/desktop-app/build/install/desktop-app/bin/desktop-app`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `common/`, `platform/`, `presentation/`, `application/`, `trade/`, etc. — core modules' in text, "expected to find: " + '- `common/`, `platform/`, `presentation/`, `application/`, `trade/`, etc. — core modules'[:80]


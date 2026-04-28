"""Behavioral checks for geodatadownloader-set-up-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/geodatadownloader")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'geodatadownloader.com (GDD) is a client-side browser application that downloads data from ArcGIS feature layers. It runs entirely in the browser with no backend, using CDN for serving static assets.' in text, "expected to find: " + 'geodatadownloader.com (GDD) is a client-side browser application that downloads data from ArcGIS feature layers. It runs entirely in the browser with no backend, using CDN for serving static assets.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Requires PUPPETEER_SKIP_DOWNLOAD=true and CYPRESS_INSTALL_BINARY=0 in CI/restricted environments' in text, "expected to find: " + '- Requires PUPPETEER_SKIP_DOWNLOAD=true and CYPRESS_INSTALL_BINARY=0 in CI/restricted environments'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Jest configuration includes setup files from both `src/` (legacy) and test files from `app/`' in text, "expected to find: " + '- Jest configuration includes setup files from both `src/` (legacy) and test files from `app/`'[:80]


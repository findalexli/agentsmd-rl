"""Behavioral checks for tootsdk-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tootsdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Tests use JSON fixtures from real server responses located in `Tests/TootSDKTests/Resources/`. Use the helper function `localObject<T>(_ type: T.Type, _ filename: String)` to load fixtures in tests.' in text, "expected to find: " + 'Tests use JSON fixtures from real server responses located in `Tests/TootSDKTests/Resources/`. Use the helper function `localObject<T>(_ type: T.Type, _ filename: String)` to load fixtures in tests.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Build**: `make build` or `swift build` (use `xcrun swift build` to avoid toolchain conflicts)' in text, "expected to find: " + '- **Build**: `make build` or `swift build` (use `xcrun swift build` to avoid toolchain conflicts)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Test data must be anonymized before inclusion (example.com domains, Lorem Ipsum content)' in text, "expected to find: " + '- Test data must be anonymized before inclusion (example.com domains, Lorem Ipsum content)'[:80]


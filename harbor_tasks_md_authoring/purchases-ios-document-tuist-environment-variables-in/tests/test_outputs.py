"""Behavioral checks for purchases-ios-document-tuist-environment-variables-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/purchases-ios")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `TUIST_LAUNCH_ARGUMENTS="-Flag1 -Flag2"` | Space-separated launch arguments injected into PaywallsTester scheme run action (enabled by default) | — |' in text, "expected to find: " + '| `TUIST_LAUNCH_ARGUMENTS="-Flag1 -Flag2"` | Space-separated launch arguments injected into PaywallsTester scheme run action (enabled by default) | — |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `TUIST_INCLUDE_TEST_DEPENDENCIES=false` | Skip test/dev dependencies (Nimble, OHHTTPStubs, etc.) to speed up `tuist install` | `true` |' in text, "expected to find: " + '| `TUIST_INCLUDE_TEST_DEPENDENCIES=false` | Skip test/dev dependencies (Nimble, OHHTTPStubs, etc.) to speed up `tuist install` | `true` |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `TUIST_SWIFT_CONDITIONS="FLAG1 FLAG2"` | Space-separated Swift compilation conditions injected into all targets | — |' in text, "expected to find: " + '| `TUIST_SWIFT_CONDITIONS="FLAG1 FLAG2"` | Space-separated Swift compilation conditions injected into all targets | — |'[:80]


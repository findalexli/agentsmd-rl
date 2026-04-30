"""Behavioral checks for webspatial-sdk-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/webspatial-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository is a `pnpm` workspace monorepo that ships WebSpatial SDK packages, a local dev/test server, and an end-to-end (AVP simulator) CI harness.' in text, "expected to find: " + 'This repository is a `pnpm` workspace monorepo that ships WebSpatial SDK packages, a local dev/test server, and an end-to-end (AVP simulator) CI harness.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `tests/ci-test`: CI/e2e harness (Mocha/Chai) that runs against the Apple Vision Pro simulator.' in text, "expected to find: " + '- `tests/ci-test`: CI/e2e harness (Mocha/Chai) that runs against the Apple Vision Pro simulator.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Keep PRs focused: avoid committing local artifacts (`.trae/`, `node_modules/`, build outputs).' in text, "expected to find: " + '- Keep PRs focused: avoid committing local artifacts (`.trae/`, `node_modules/`, build outputs).'[:80]


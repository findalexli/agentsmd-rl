"""Behavioral checks for evmone-add-agentsmd-with-review-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/evmone")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Crypto misuse (non-constant-time operations on secrets, weak randomness, incorrect nonce handling, missing domain separation, insecure parameters).' in text, "expected to find: " + '- Crypto misuse (non-constant-time operations on secrets, weak randomness, incorrect nonce handling, missing domain separation, insecure parameters).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Other suggestions and improvements are welcome as long as they are constructive, actionable, and help improve quality, security, and maintainability.' in text, "expected to find: " + 'Other suggestions and improvements are welcome as long as they are constructive, actionable, and help improve quality, security, and maintainability.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When reviewing changes (code, tests, build scripts, documentation, workflows), expand the review beyond correctness and style. Actively look for:' in text, "expected to find: " + 'When reviewing changes (code, tests, build scripts, documentation, workflows), expand the review beyond correctness and style. Actively look for:'[:80]


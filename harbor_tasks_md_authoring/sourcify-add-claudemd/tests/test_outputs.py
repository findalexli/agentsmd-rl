"""Behavioral checks for sourcify-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sourcify")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Sourcify is an open-source smart contract verification service for Ethereum and compatible blockchains. The repository is a monorepo containing:' in text, "expected to find: " + 'Sourcify is an open-source smart contract verification service for Ethereum and compatible blockchains. The repository is a monorepo containing:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'IMPORTANT: Double check the `.env` file in `services/database` and ask for approval before running any `npm run migrate` commands' in text, "expected to find: " + 'IMPORTANT: Double check the `.env` file in `services/database` and ask for approval before running any `npm run migrate` commands'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **services/monitor**: Chain monitoring service that automatically detects new contracts and submits them for verification' in text, "expected to find: " + '- **services/monitor**: Chain monitoring service that automatically detects new contracts and submits them for verification'[:80]


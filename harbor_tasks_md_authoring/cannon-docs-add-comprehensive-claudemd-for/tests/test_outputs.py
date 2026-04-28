"""Behavioral checks for cannon-docs-add-comprehensive-claudemd-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cannon")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Cannon is a DevOps tool for EVM chains designed for testing, deploying, and publishing smart contracts. This is a monorepo structured around a core builder engine with multiple packages and applicatio' in text, "expected to find: " + 'Cannon is a DevOps tool for EVM chains designed for testing, deploying, and publishing smart contracts. This is a monorepo structured around a core builder engine with multiple packages and applicatio'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Cannonfiles** (cannonfile.toml) - TOML configuration files defining deployment workflows with actions like `deploy`, `invoke`, `var`' in text, "expected to find: " + '- **Cannonfiles** (cannonfile.toml) - TOML configuration files defining deployment workflows with actions like `deploy`, `invoke`, `var`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Chain Builder Runtime** - Executes deployment steps against blockchain networks, handling dependencies automatically' in text, "expected to find: " + '- **Chain Builder Runtime** - Executes deployment steps against blockchain networks, handling dependencies automatically'[:80]


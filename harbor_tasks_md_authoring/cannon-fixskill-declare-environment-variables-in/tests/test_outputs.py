"""Behavioral checks for cannon-fixskill-declare-environment-variables-in (markdown_authoring task).

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
    text = _read('packages/skill/SKILL.md')
    assert '| `CANNON_ETHERSCAN_API_KEY` | Etherscan API key for contract verification (`cannon verify`). Required for verifying deployed contracts on Etherscan-supported chains. |' in text, "expected to find: " + '| `CANNON_ETHERSCAN_API_KEY` | Etherscan API key for contract verification (`cannon verify`). Required for verifying deployed contracts on Etherscan-supported chains. |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/skill/SKILL.md')
    assert '| `CANNON_PRIVATE_KEY` | Private key for signing on-chain transactions (deploy, publish, register). Required for non-dry-run operations on real networks. |' in text, "expected to find: " + '| `CANNON_PRIVATE_KEY` | Private key for signing on-chain transactions (deploy, publish, register). Required for non-dry-run operations on real networks. |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/skill/SKILL.md')
    assert '| `CANNON_DIRECTORY` | Custom directory for Cannon package storage and build artifacts. Defaults to `~/.local/share/cannon/` if not set. |' in text, "expected to find: " + '| `CANNON_DIRECTORY` | Custom directory for Cannon package storage and build artifacts. Defaults to `~/.local/share/cannon/` if not set. |'[:80]


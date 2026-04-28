"""Behavioral checks for operator-lifecycle-manager-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/operator-lifecycle-manager")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Operator Lifecycle Manager (OLM) extends Kubernetes to provide declarative installation, upgrade, and lifecycle management for Kubernetes operators. It's part of the [Operator Framework](https://githu" in text, "expected to find: " + "Operator Lifecycle Manager (OLM) extends Kubernetes to provide declarative installation, upgrade, and lifecycle management for Kubernetes operators. It's part of the [Operator Framework](https://githu"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**CRITICAL**: This repository is in **maintenance mode**. OLM v0 accepts only critical bug fixes and security updates. For new development, use [operator-controller](https://github.com/operator-framew' in text, "expected to find: " + '**CRITICAL**: This repository is in **maintenance mode**. OLM v0 accepts only critical bug fixes and security updates. For new development, use [operator-controller](https://github.com/operator-framew'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This file provides AI agents with comprehensive context about the Operator Lifecycle Manager (OLM) v0 codebase to enable effective navigation, understanding, and contribution.' in text, "expected to find: " + 'This file provides AI agents with comprehensive context about the Operator Lifecycle Manager (OLM) v0 codebase to enable effective navigation, understanding, and contribution.'[:80]


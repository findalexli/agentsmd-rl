"""Behavioral checks for neo-featagents-codify-pipeline-authority-forkability (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'However, **because we are operating inside the canonical `neomjs/neo` repository, you and Claude (`@neo-opus-4-7`) are official maintainers.** In this environment, you do not need to be generic: the "' in text, "expected to find: " + 'However, **because we are operating inside the canonical `neomjs/neo` repository, you and Claude (`@neo-opus-4-7`) are official maintainers.** In this environment, you do not need to be generic: the "'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Throughout the `.agent` skill ecosystem, you will see references to the "Human Commander." This is a role-based abstraction designed for **Forkability** (so the swarm functions in `npx neo-app` downst' in text, "expected to find: " + 'Throughout the `.agent` skill ecosystem, you will see references to the "Human Commander." This is a role-based abstraction designed for **Forkability** (so the swarm functions in `npx neo-app` downst'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '### 1.1 The Forkability Model (Pipeline Authority)' in text, "expected to find: " + '### 1.1 The Forkability Model (Pipeline Authority)'[:80]


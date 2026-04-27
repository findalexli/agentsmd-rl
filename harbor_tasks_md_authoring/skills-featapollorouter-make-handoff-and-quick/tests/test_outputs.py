"""Behavioral checks for skills-featapollorouter-make-handoff-and-quick (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/apollo-router/SKILL.md')
    assert '- Local supergraph path: use `graphql-schema` + `apollo-server` to define/run subgraphs, then use `graphql-operations` for smoke tests, then use the `rover` skill to compose or fetch `supergraph.graph' in text, "expected to find: " + '- Local supergraph path: use `graphql-schema` + `apollo-server` to define/run subgraphs, then use `graphql-operations` for smoke tests, then use the `rover` skill to compose or fetch `supergraph.graph'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/apollo-router/SKILL.md')
    assert 'If prerequisites are missing or unknown, end with a concise **Next steps** handoff (1-3 lines max) that is skill-first and command-free:' in text, "expected to find: " + 'If prerequisites are missing or unknown, end with a concise **Next steps** handoff (1-3 lines max) that is skill-first and command-free:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/apollo-router/SKILL.md')
    assert '- MUST state that Rover is required only for the local supergraph path; GraphOS-managed runtime does not require local Rover composition' in text, "expected to find: " + '- MUST state that Rover is required only for the local supergraph path; GraphOS-managed runtime does not require local Rover composition'[:80]


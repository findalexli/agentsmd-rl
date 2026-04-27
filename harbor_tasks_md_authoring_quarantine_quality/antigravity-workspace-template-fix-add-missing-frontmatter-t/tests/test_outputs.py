"""Behavioral checks for antigravity-workspace-template-fix-add-missing-frontmatter-t (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-workspace-template")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('engine/antigravity_engine/skills/agent-repo-init/SKILL.md')
    assert 'description: Bootstraps a new multi-agent repository from the Antigravity template via `init_agent_repo`. Supports quick scaffold and full runtime profile setup including LLM provider, MCP toggle, swa' in text, "expected to find: " + 'description: Bootstraps a new multi-agent repository from the Antigravity template via `init_agent_repo`. Supports quick scaffold and full runtime profile setup including LLM provider, MCP toggle, swa'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('engine/antigravity_engine/skills/agent-repo-init/SKILL.md')
    assert 'name: agent-repo-init' in text, "expected to find: " + 'name: agent-repo-init'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('engine/antigravity_engine/skills/graph-retrieval/SKILL.md')
    assert 'description: Exposes graph-based retrieval as a tool capability via `query_graph`. Reads normalized graph store files, builds a query-relevant subgraph, and returns LLM-friendly semantic triples with ' in text, "expected to find: " + 'description: Exposes graph-based retrieval as a tool capability via `query_graph`. Reads normalized graph store files, builds a query-relevant subgraph, and returns LLM-friendly semantic triples with '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('engine/antigravity_engine/skills/graph-retrieval/SKILL.md')
    assert 'name: graph-retrieval' in text, "expected to find: " + 'name: graph-retrieval'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('engine/antigravity_engine/skills/knowledge-layer/SKILL.md')
    assert 'description: High-level deployment wrapper over Antigravity core with graph-first knowledge injection and all-file support. Exposes `refresh_filesystem` and `ask_filesystem` for building and querying ' in text, "expected to find: " + 'description: High-level deployment wrapper over Antigravity core with graph-first knowledge injection and all-file support. Exposes `refresh_filesystem` and `ask_filesystem` for building and querying '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('engine/antigravity_engine/skills/knowledge-layer/SKILL.md')
    assert 'name: knowledge-layer' in text, "expected to find: " + 'name: knowledge-layer'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('engine/antigravity_engine/skills/research/SKILL.md')
    assert 'description: Performs deep research on a topic via `deep_research`. Simulates a multi-step research process and returns a comprehensive research result as a string.' in text, "expected to find: " + 'description: Performs deep research on a topic via `deep_research`. Simulates a multi-step research process and returns a comprehensive research result as a string.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('engine/antigravity_engine/skills/research/SKILL.md')
    assert 'name: research' in text, "expected to find: " + 'name: research'[:80]


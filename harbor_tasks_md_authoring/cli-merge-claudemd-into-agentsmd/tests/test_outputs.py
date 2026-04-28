"""Behavioral checks for cli-merge-claudemd-into-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is the Databricks CLI, a command-line interface for interacting with Databricks workspaces and managing Databricks Assets Bundles (DABs). The project is written in Go and follows a modular archit' in text, "expected to find: " + 'This is the Databricks CLI, a command-line interface for interacting with Databricks workspaces and managing Databricks Assets Bundles (DABs). The project is written in Go and follows a modular archit'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Bundles**: Configuration-driven deployments of Databricks resources (jobs, pipelines, etc.). The bundle system uses a mutator pattern where each transformation is a separate, testable component.' in text, "expected to find: " + '**Bundles**: Configuration-driven deployments of Databricks resources (jobs, pipelines, etc.). The bundle system uses a mutator pattern where each transformation is a separate, testable component.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Mutators**: Transform bundle configuration through a pipeline. Located in `bundle/config/mutator/` and `bundle/mutator/`. Each mutator implements the `Mutator` interface.' in text, "expected to find: " + '**Mutators**: Transform bundle configuration through a pipeline. Located in `bundle/config/mutator/` and `bundle/mutator/`. Each mutator implements the `Mutator` interface.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


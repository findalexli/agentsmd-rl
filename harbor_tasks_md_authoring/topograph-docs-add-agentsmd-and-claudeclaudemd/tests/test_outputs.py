"""Behavioral checks for topograph-docs-add-agentsmd-and-claudeclaudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/topograph")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'A provider returns the root `*topology.Vertex` of the discovered tree. Leaf vertices are compute nodes; interior vertices are switches or (for block topology) accelerator domains. Return `*httperr.Err' in text, "expected to find: " + 'A provider returns the root `*topology.Vertex` of the discovered tree. Leaf vertices are compute nodes; interior vertices are switches or (for block topology) accelerator domains. Return `*httperr.Err'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'Engines are much rarer (three exist: slurm, k8s, slinky). Follow the same registry pattern but register in `engines.NewRegistry(...)`. Coordinate with maintainers before starting — adding an engine im' in text, "expected to find: " + 'Engines are much rarer (three exist: slurm, k8s, slinky). Follow the same registry pattern but register in `engines.NewRegistry(...)`. Coordinate with maintainers before starting — adding an engine im'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'Topograph discovers the physical network topology of a cluster (NVLink domains, InfiniBand/Ethernet switch fabric, cloud rack topology) and exposes it to workload schedulers — Slurm, Kubernetes, and S' in text, "expected to find: " + 'Topograph discovers the physical network topology of a cluster (NVLink domains, InfiniBand/Ethernet switch fabric, cloud rack topology) and exposes it to workload schedulers — Slurm, Kubernetes, and S'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'A provider returns the root `*topology.Vertex` of the discovered tree. Leaf vertices are compute nodes; interior vertices are switches or (for block topology) accelerator domains. Return `*httperr.Err' in text, "expected to find: " + 'A provider returns the root `*topology.Vertex` of the discovered tree. Leaf vertices are compute nodes; interior vertices are switches or (for block topology) accelerator domains. Return `*httperr.Err'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Engines are much rarer (three exist: slurm, k8s, slinky). Follow the same registry pattern but register in `engines.NewRegistry(...)`. Coordinate with maintainers before starting — adding an engine im' in text, "expected to find: " + 'Engines are much rarer (three exist: slurm, k8s, slinky). Follow the same registry pattern but register in `engines.NewRegistry(...)`. Coordinate with maintainers before starting — adding an engine im'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Topograph discovers the physical network topology of a cluster (NVLink domains, InfiniBand/Ethernet switch fabric, cloud rack topology) and exposes it to workload schedulers — Slurm, Kubernetes, and S' in text, "expected to find: " + 'Topograph discovers the physical network topology of a cluster (NVLink domains, InfiniBand/Ethernet switch fabric, cloud rack topology) and exposes it to workload schedulers — Slurm, Kubernetes, and S'[:80]


"""Behavioral checks for kubernetes-mcp-server-featai-add-claudemd-instructions-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kubernetes-mcp-server")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Each toolset lives in its own subdirectory under `pkg/toolsets/` (e.g., `pkg/toolsets/config/`, `pkg/toolsets/core/`, `pkg/toolsets/helm/`).' in text, "expected to find: " + '- Each toolset lives in its own subdirectory under `pkg/toolsets/` (e.g., `pkg/toolsets/config/`, `pkg/toolsets/core/`, `pkg/toolsets/helm/`).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Toolsets** group related tools together (e.g., config tools, core Kubernetes tools, Helm tools).' in text, "expected to find: " + '- **Toolsets** group related tools together (e.g., config tools, core Kubernetes tools, Helm tools).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Registration** happens in `pkg/toolsets/` where toolsets are registered at initialization.' in text, "expected to find: " + '- **Registration** happens in `pkg/toolsets/` where toolsets are registered at initialization.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


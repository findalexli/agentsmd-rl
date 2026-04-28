"""Behavioral checks for testkube-chore-init-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/testkube")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Helm chart values are the source of deployment defaults; `build/_local/values.dev.yaml` (shaped by the `values.dev.tpl.yaml` template) shows the local overrides used by `tk-dev` if you need a concre' in text, "expected to find: " + '- Helm chart values are the source of deployment defaults; `build/_local/values.dev.yaml` (shaped by the `values.dev.tpl.yaml` template) shows the local overrides used by `tk-dev` if you need a concre'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Exposes tools across workflows, executions, artifacts, and metadata via `testkube mcp serve` (CLI), Docker image (`testkube/mcp-server`), or Control Plane's `/mcp` endpoint per environment." in text, "expected to find: " + "- Exposes tools across workflows, executions, artifacts, and metadata via `testkube mcp serve` (CLI), Docker image (`testkube/mcp-server`), or Control Plane's `/mcp` endpoint per environment."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `cmd/api-server` is the main agent API server; agent personas (superagent, runner, listener, GitOps, etc.) are enabled through Helm values and env configuration.' in text, "expected to find: " + '- `cmd/api-server` is the main agent API server; agent personas (superagent, runner, listener, GitOps, etc.) are enabled through Helm values and env configuration.'[:80]


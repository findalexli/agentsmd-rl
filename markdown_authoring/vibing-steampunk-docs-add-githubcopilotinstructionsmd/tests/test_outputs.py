"""Behavioral checks for vibing-steampunk-docs-add-githubcopilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vibing-steampunk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Safety system**: All write operations check `SafetyConfig` before execution. Operation types are single-letter codes: R(ead), S(earch), Q(uery), F(ree SQL), C(reate), U(pdate), D(elete), A(ctivate' in text, "expected to find: " + '- **Safety system**: All write operations check `SafetyConfig` before execution. Operation types are single-letter codes: R(ead), S(earch), Q(uery), F(ree SQL), C(reate), U(pdate), D(elete), A(ctivate'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**vsp** is a Go-native MCP (Model Context Protocol) server that bridges AI agents to SAP ABAP systems via the ADT REST API. Single binary, 9 platforms, zero dependencies. It exposes 81 tools (focused ' in text, "expected to find: " + '**vsp** is a Go-native MCP (Model Context Protocol) server that bridges AI agents to SAP ABAP systems via the ADT REST API. Single binary, 9 platforms, zero dependencies. It exposes 81 tools (focused '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Integration tests** use build tag `integration` and require `SAP_URL`, `SAP_USER`, `SAP_PASSWORD`, `SAP_CLIENT` env vars. They create objects in the `$TMP` package and clean up after themselves.' in text, "expected to find: " + '- **Integration tests** use build tag `integration` and require `SAP_URL`, `SAP_USER`, `SAP_PASSWORD`, `SAP_CLIENT` env vars. They create objects in the `$TMP` package and clean up after themselves.'[:80]


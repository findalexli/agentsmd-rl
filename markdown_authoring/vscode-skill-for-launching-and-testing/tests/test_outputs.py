"""Behavioral checks for vscode-skill-for-launching-and-testing (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vscode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/vscode-dev-workbench/SKILL.md')
    assert '`--enable-mock-agent` registers the `ScriptedMockAgent` from `src/vs/platform/agentHost/test/node/mockAgent.ts` with one pre-existing session. Seed additional sessions via the `VSCODE_AGENT_HOST_MOCK_' in text, "expected to find: " + '`--enable-mock-agent` registers the `ScriptedMockAgent` from `src/vs/platform/agentHost/test/node/mockAgent.ts` with one pre-existing session. Seed additional sessions via the `VSCODE_AGENT_HOST_MOCK_'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/vscode-dev-workbench/SKILL.md')
    assert 'This bypasses GitHub auth and the `/agents/api/hosts` endpoint entirely, so it works offline. The fake tunnel on the `vscode-dev` side must advertise a `protocolvN` tag ≥ `TUNNEL_MIN_PROTOCOL_VERSION`' in text, "expected to find: " + 'This bypasses GitHub auth and the `/agents/api/hosts` endpoint entirely, so it works offline. The fake tunnel on the `vscode-dev` side must advertise a `protocolvN` tag ≥ `TUNNEL_MIN_PROTOCOL_VERSION`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/vscode-dev-workbench/SKILL.md')
    assert 'description: Use when the user wants to run the vscode.dev server locally and exercise the VS Code workbench or Agents window in the integrated browser against the local `microsoft/vscode` sources. Co' in text, "expected to find: " + 'description: Use when the user wants to run the vscode.dev server locally and exercise the VS Code workbench or Agents window in the integrated browser against the local `microsoft/vscode` sources. Co'[:80]


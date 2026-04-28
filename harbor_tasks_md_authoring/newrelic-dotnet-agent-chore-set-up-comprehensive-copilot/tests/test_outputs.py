"""Behavioral checks for newrelic-dotnet-agent-chore-set-up-comprehensive-copilot (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/newrelic-dotnet-agent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This repository contains the New Relic .NET Agent, which monitors .NET applications and provides performance insights. The agent supports both .NET Framework and .NET Core/.NET applications on Windows' in text, "expected to find: " + 'This repository contains the New Relic .NET Agent, which monitors .NET applications and provides performance insights. The agent supports both .NET Framework and .NET Core/.NET applications on Windows'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- The agent runs in customer application processes - **it must not crash, destabilize, or significantly degrade performance**' in text, "expected to find: " + '- The agent runs in customer application processes - **it must not crash, destabilize, or significantly degrade performance**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **FullAgent.sln**: Main solution containing the managed C# code for the agent, including all unit tests' in text, "expected to find: " + '- **FullAgent.sln**: Main solution containing the managed C# code for the agent, including all unit tests'[:80]


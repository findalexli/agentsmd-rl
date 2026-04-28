"""Behavioral checks for debos-add-githubcopilotinstructionsmd-for-agent-onboarding (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/debos")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Integration tests:** Integration/recipe tests run in Docker containers with fakemachine and require privileged access and KVM. Before submitting changes, run relevant integration test recipes, espec' in text, "expected to find: " + '**Integration tests:** Integration/recipe tests run in Docker containers with fakemachine and require privileged access and KVM. Before submitting changes, run relevant integration test recipes, espec'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**debos** is a tool for creating Debian-based OS images. It reads YAML recipe files and executes actions sequentially to build customized OS images. It uses fakemachine (a virtualization backend) to e' in text, "expected to find: " + '**debos** is a tool for creating Debian-based OS images. It reads YAML recipe files and executes actions sequentially to build customized OS images. It uses fakemachine (a virtualization backend) to e'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Note:** The action lifecycle differs when running with or without fakemachine (--disable-fakemachine). PreMachine is called when using fakemachine, while PreNoMachine is called when not using fakema' in text, "expected to find: " + '**Note:** The action lifecycle differs when running with or without fakemachine (--disable-fakemachine). PreMachine is called when using fakemachine, while PreNoMachine is called when not using fakema'[:80]


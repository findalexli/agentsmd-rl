"""Behavioral checks for spice86-chore-copilot-instructions-to-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/spice86")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Spice86 is a .NET 8 cross-platform emulator for reverse engineering real-mode DOS programs. It enables running, analyzing, and incrementally rewriting DOS binaries in C# without source code.' in text, "expected to find: " + 'Spice86 is a .NET 8 cross-platform emulator for reverse engineering real-mode DOS programs. It enables running, analyzing, and incrementally rewriting DOS binaries in C# without source code.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '2. Emulator dumps `spice86dumpMemoryDump.bin` and `spice86dumpExecutionFlow.json` to `--RecordedDataDirectory`' in text, "expected to find: " + '2. Emulator dumps `spice86dumpMemoryDump.bin` and `spice86dumpExecutionFlow.json` to `--RecordedDataDirectory`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Documentation**: XML comments required (`<GenerateDocumentationFile>true</GenerateDocumentationFile>`)' in text, "expected to find: " + '- **Documentation**: XML comments required (`<GenerateDocumentationFile>true</GenerateDocumentationFile>`)'[:80]


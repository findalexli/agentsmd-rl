"""Behavioral checks for vscode-makefile-tools-create-copilotinstructionsmd-for-makef (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vscode-makefile-tools")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'description: "You are an expert contributor to microsoft/vscode-makefile-tools, a TypeScript VS Code extension for Makefile-based C/C++ projects targeting Windows, macOS, and Linux. You are deeply fam' in text, "expected to find: " + 'description: "You are an expert contributor to microsoft/vscode-makefile-tools, a TypeScript VS Code extension for Makefile-based C/C++ projects targeting Windows, macOS, and Linux. You are deeply fam'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Core mechanism**: The extension runs `make --dry-run` (or reads a pre-generated build log) to capture compiler invocations without actually building. `parser.ts` extracts source files, includes, d' in text, "expected to find: " + '- **Core mechanism**: The extension runs `make --dry-run` (or reads a pre-generated build log) to capture compiler invocations without actually building. `parser.ts` extracts source files, includes, d'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Configuration priority**: When resolving make parameters, the extension follows a strict priority chain (defined at the top of `configuration.ts`): (1) `makefile.configurations[].buildLog` → (2) `' in text, "expected to find: " + '- **Configuration priority**: When resolving make parameters, the extension follows a strict priority chain (defined at the top of `configuration.ts`): (1) `makefile.configurations[].buildLog` → (2) `'[:80]


"""Behavioral checks for vscode-spell-checker-add-githubcopilotinstructionsmd-for-cop (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vscode-spell-checker")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This repository contains **Code Spell Checker**, a VS Code extension that performs spell checking for source code. It uses a client/server architecture: the VS Code extension client communicates with ' in text, "expected to find: " + 'This repository contains **Code Spell Checker**, a VS Code extension that performs spell checking for source code. It uses a client/server architecture: the VS Code extension client communicates with '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "- **`.mts` files**: Most TypeScript source files use the `.mts` extension. Import paths must use `.mjs` extensions (e.g., `import { foo } from './foo.mjs'`) in `.mts` files because of `NodeNext` modul" in text, "expected to find: " + "- **`.mts` files**: Most TypeScript source files use the `.mts` extension. Import paths must use `.mjs` extensions (e.g., `import { foo } from './foo.mjs'`) in `.mts` files because of `NodeNext` modul"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- The **client** (`packages/client`) runs inside the VS Code extension host and communicates with the **server** (`packages/_server`) over JSON-RPC using the VS Code Language Client library.' in text, "expected to find: " + '- The **client** (`packages/client`) runs inside the VS Code extension host and communicates with the **server** (`packages/_server`) over JSON-RPC using the VS Code Language Client library.'[:80]


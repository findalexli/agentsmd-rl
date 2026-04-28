"""Behavioral checks for risuai-feat-add-agentsmd-for-project (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/risuai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'RisuAI is a cross-platform AI chatting software built with Svelte, TypeScript, and Tauri. It allows users to chat with various AI models through a single application. The application supports multiple' in text, "expected to find: " + 'RisuAI is a cross-platform AI chatting software built with Svelte, TypeScript, and Tauri. It allows users to chat with various AI models through a single application. The application supports multiple'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The project is structured as a monorepo with the frontend application in the `src` directory and the Tauri-specific code in the `src-tauri` directory. The frontend is built using Vite, and the applica' in text, "expected to find: " + 'The project is structured as a monorepo with the frontend application in the `src` directory and the Tauri-specific code in the `src-tauri` directory. The frontend is built using Vite, and the applica'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Please follow the existing coding style and conventions when contributing to the project. Ensure that your code is well-tested and that you have run the type checker before submitting a pull request.' in text, "expected to find: " + 'Please follow the existing coding style and conventions when contributing to the project. Ensure that your code is well-tested and that you have run the type checker before submitting a pull request.'[:80]


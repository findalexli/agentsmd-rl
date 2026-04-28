"""Behavioral checks for vscode-csharp-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vscode-csharp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `src/lsptoolshost/copilot/contextProviders.ts` and `relatedFilesProvider.ts` register C# context and related files providers for GitHub Copilot and Copilot Chat extensions.' in text, "expected to find: " + '- `src/lsptoolshost/copilot/contextProviders.ts` and `relatedFilesProvider.ts` register C# context and related files providers for GitHub Copilot and Copilot Chat extensions.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **TypeScript**: Follows strict linting (`.eslintrc.js`), including header/license blocks and camelCase filenames (except for interfaces and special files).' in text, "expected to find: " + '- **TypeScript**: Follows strict linting (`.eslintrc.js`), including header/license blocks and camelCase filenames (except for interfaces and special files).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Task Patterns**: Use `projectPaths.ts` for consistent path references, follow existing naming conventions (`test:integration:*`, `vsix:*`, etc.)' in text, "expected to find: " + '- **Task Patterns**: Use `projectPaths.ts` for consistent path references, follow existing naming conventions (`test:integration:*`, `vsix:*`, etc.)'[:80]


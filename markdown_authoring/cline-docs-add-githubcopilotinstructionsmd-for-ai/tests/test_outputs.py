"""Behavioral checks for cline-docs-add-githubcopilotinstructionsmd-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cline")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Adding a key requires: type in `src/shared/storage/state-keys.ts`, read via `context.globalState.get()` in `src/core/storage/utils/state-helpers.ts` `readGlobalStateFromDisk()`, and add to return obje' in text, "expected to find: " + 'Adding a key requires: type in `src/shared/storage/state-keys.ts`, read via `context.globalState.get()` in `src/core/storage/utils/state-helpers.ts` `readGlobalStateFromDisk()`, and add to return obje'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Modular: `components/` (shared) + `variants/` (model-specific) + `templates/` (`{{PLACEHOLDER}}`). Variants override components via `componentOverrides` in `config.ts` or custom `template.ts`. XS vari' in text, "expected to find: " + 'Modular: `components/` (shared) + `variants/` (model-specific) + `templates/` (`{{PLACEHOLDER}}`). Variants override components via `componentOverrides` in `config.ts` or custom `template.ts`. XS vari'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Also update: `src/shared/api.ts`, `src/shared/providers/providers.json`, `src/core/api/index.ts`, `webview-ui/.../providerUtils.ts`, `webview-ui/.../validate.ts`, `webview-ui/.../ApiOptions.tsx`, and ' in text, "expected to find: " + 'Also update: `src/shared/api.ts`, `src/shared/providers/providers.json`, `src/core/api/index.ts`, `webview-ui/.../providerUtils.ts`, `webview-ui/.../validate.ts`, `webview-ui/.../ApiOptions.tsx`, and '[:80]


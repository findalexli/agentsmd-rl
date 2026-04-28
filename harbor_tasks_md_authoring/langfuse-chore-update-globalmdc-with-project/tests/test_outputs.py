"""Behavioral checks for langfuse-chore-update-globalmdc-with-project (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/langfuse")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/global.mdc')
    assert 'The most important domain objects are in [observations.ts](mdc:packages/shared/src/domain/observations.ts), [traces.ts](mdc:packages/shared/src/domain/traces.ts), [scores.ts](mdc:packages/shared/src/d' in text, "expected to find: " + 'The most important domain objects are in [observations.ts](mdc:packages/shared/src/domain/observations.ts), [traces.ts](mdc:packages/shared/src/domain/traces.ts), [scores.ts](mdc:packages/shared/src/d'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/global.mdc')
    assert '- Before finishing a task, please run prettier via `pnpm format` to format the code of the repository. Otherwise, the CI check will fail on the change.' in text, "expected to find: " + '- Before finishing a task, please run prettier via `pnpm format` to format the code of the repository. Otherwise, the CI check will fail on the change.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/global.mdc')
    assert 'When running in a background/cloud agent, please adhere to the following rules:' in text, "expected to find: " + 'When running in a background/cloud agent, please adhere to the following rules:'[:80]


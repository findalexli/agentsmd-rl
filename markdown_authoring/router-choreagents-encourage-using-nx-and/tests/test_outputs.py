"""Behavioral checks for router-choreagents-encourage-using-nx-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/router")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Example workflow:** `pnpm nx run @tanstack/react-router:test:unit` → `pnpm nx run @tanstack/react-router:test:unit -- tests/link.test.tsx` → `pnpm nx run @tanstack/react-router:test:unit -- tests/' in text, "expected to find: " + '- **Example workflow:** `pnpm nx run @tanstack/react-router:test:unit` → `pnpm nx run @tanstack/react-router:test:unit -- tests/link.test.tsx` → `pnpm nx run @tanstack/react-router:test:unit -- tests/'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Testing strategy:** Package level (nx) → File-level args via nx → Test-level args (`-t`) via nx → Pattern-level args (`--exclude`) via nx' in text, "expected to find: " + '- **Testing strategy:** Package level (nx) → File-level args via nx → Test-level args (`-t`) via nx → Pattern-level args (`--exclude`) via nx'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Do not loop retries indefinitely. If it still hangs or sandbox blocks graph/daemon behavior, request escalation immediately.' in text, "expected to find: " + '- Do not loop retries indefinitely. If it still hangs or sandbox blocks graph/daemon behavior, request escalation immediately.'[:80]


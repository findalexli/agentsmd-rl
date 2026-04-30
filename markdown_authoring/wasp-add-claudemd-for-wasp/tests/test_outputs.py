"""Behavioral checks for wasp-add-claudemd-for-wasp (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wasp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'All waspc development commands run from the `waspc/` directory via the `./run` script. Run `./run` with no arguments to see the full list of available commands (build, test, format, lint, etc.).' in text, "expected to find: " + 'All waspc development commands run from the `waspc/` directory via the `./run` script. Run `./run` with no arguments to see the full list of available commands (build, test, format, lint, etc.).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **E2E snapshots** (`waspc/e2e-tests/test-outputs/snapshots/`) must never be manually edited. Regenerate them by running `cd waspc && ./run build && ./run test:waspc:e2e:accept-all`.' in text, "expected to find: " + '- **E2E snapshots** (`waspc/e2e-tests/test-outputs/snapshots/`) must never be manually edited. Regenerate them by running `cd waspc && ./run build && ./run test:waspc:e2e:accept-all`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Two-phase build: TS packages in `data/packages/` and libs in `data/Generator/libs/` compile first, then Haskell (which embeds them). Use `./run build` for the full build.' in text, "expected to find: " + '- Two-phase build: TS packages in `data/packages/` and libs in `data/Generator/libs/` compile first, then Haskell (which embeds them). Use `./run build` for the full build.'[:80]


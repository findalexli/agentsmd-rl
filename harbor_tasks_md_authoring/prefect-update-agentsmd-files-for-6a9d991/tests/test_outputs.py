"""Behavioral checks for prefect-update-agentsmd-files-for-6a9d991 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prefect")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/runner/AGENTS.md')
    assert '- **`directories`** entries starting with `--` trigger a `UserWarning` but are not rejected. The values are passed to `git sparse-checkout set --` (with a `--` separator to prevent flag injection). Th' in text, "expected to find: " + '- **`directories`** entries starting with `--` trigger a `UserWarning` but are not rejected. The values are passed to `git sparse-checkout set --` (with a `--` separator to prevent flag injection). Th'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/runner/AGENTS.md')
    assert '- **`commit_sha`** must match `^[0-9a-fA-F]{4,64}$` — any value that fails (including git option strings like `--upload-pack=...`) raises `ValueError`. Branch/tag names must use the `branch` parameter' in text, "expected to find: " + '- **`commit_sha`** must match `^[0-9a-fA-F]{4,64}$` — any value that fails (including git option strings like `--upload-pack=...`) raises `ValueError`. Branch/tag names must use the `branch` parameter'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/runner/AGENTS.md')
    assert 'These validations exist to prevent git argument injection. Do not bypass them when constructing `GitRepository` programmatically.' in text, "expected to find: " + 'These validations exist to prevent git argument injection. Do not bypass them when constructing `GitRepository` programmatically.'[:80]


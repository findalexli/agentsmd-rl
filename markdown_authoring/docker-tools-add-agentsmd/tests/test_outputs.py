"""Behavioral checks for docker-tools-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/docker-tools")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Manifest files define metadata about which Docker images ImageBuilder will build. The schema is defined by the `Manifest` model in `src/ImageBuilder.Models/Manifest/Manifest.cs`. For detailed document' in text, "expected to find: " + 'Manifest files define metadata about which Docker images ImageBuilder will build. The schema is defined by the `Manifest` model in `src/ImageBuilder.Models/Manifest/Manifest.cs`. For detailed document'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'To test ImageBuilder code changes and pipeline template changes together without waiting for the two-step process, use the `bootstrapImageBuilder` parameter in the unofficial pipeline (`eng/pipelines/' in text, "expected to find: " + 'To test ImageBuilder code changes and pipeline template changes together without waiting for the two-step process, use the `bootstrapImageBuilder` parameter in the unofficial pipeline (`eng/pipelines/'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Commands** (`src/ImageBuilder/Commands/`) - Each command implements a specific operation (build, publish, generateBuildMatrix, etc.). Commands inherit from `Command<TOptions>` and use System.Comma' in text, "expected to find: " + '- **Commands** (`src/ImageBuilder/Commands/`) - Each command implements a specific operation (build, publish, generateBuildMatrix, etc.). Commands inherit from `Command<TOptions>` and use System.Comma'[:80]


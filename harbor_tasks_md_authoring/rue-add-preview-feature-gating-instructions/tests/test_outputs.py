"""Behavioral checks for rue-add-preview-feature-gating-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rue")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**IMPORTANT**: New language features MUST be gated behind preview flags until complete. See [ADR-0005](docs/designs/0005-preview-features.md) for the full design.' in text, "expected to find: " + '**IMPORTANT**: New language features MUST be gated behind preview flags until complete. See [ADR-0005](docs/designs/0005-preview-features.md) for the full design.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**This is the critical step that actually gates the feature!** Without this call, users can use the feature without `--preview`.' in text, "expected to find: " + '**This is the critical step that actually gates the feature!** Without this call, users can use the feature without `--preview`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'self.require_preview(PreviewFeature::YourNewFeature, "your feature description", span)?;' in text, "expected to find: " + 'self.require_preview(PreviewFeature::YourNewFeature, "your feature description", span)?;'[:80]


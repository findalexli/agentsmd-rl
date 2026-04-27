"""Behavioral checks for skills-model-migration-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-model-migration/SKILL.md')
    assert 'description: "Guides embedding model migration in Qdrant without downtime. Use when someone asks \'how to switch embedding models\', \'how to migrate vectors\', \'how to update to a new model\', \'zero-downt' in text, "expected to find: " + 'description: "Guides embedding model migration in Qdrant without downtime. Use when someone asks \'how to switch embedding models\', \'how to migrate vectors\', \'how to update to a new model\', \'zero-downt'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-model-migration/SKILL.md')
    assert 'You CAN avoid re-embedding if: using Matryoshka models (use `dimensions` parameter to output lower-dimensional embeddings, learn linear transformation from sample data, some recall loss, good for 100M' in text, "expected to find: " + 'You CAN avoid re-embedding if: using Matryoshka models (use `dimensions` parameter to output lower-dimensional embeddings, learn linear transformation from sample data, some recall loss, good for 100M'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-model-migration/SKILL.md')
    assert 'Vectors from different models are incompatible. You cannot mix old and new embeddings in the same vector space. You also cannot add new named vector fields to an existing collection. All named vectors' in text, "expected to find: " + 'Vectors from different models are incompatible. You cannot mix old and new embeddings in the same vector space. You also cannot add new named vector fields to an existing collection. All named vectors'[:80]


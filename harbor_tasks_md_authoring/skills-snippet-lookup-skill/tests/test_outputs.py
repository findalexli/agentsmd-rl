"""Behavioral checks for skills-snippet-lookup-skill (markdown_authoring task).

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
    text = _read('skills/qdrant-clients-sdk/SKILL.md')
    assert 'Uploads multiple vector-embedded points to a Qdrant collection using the Python qdrant_client (PointStruct) with id, payload (e.g., color), and a 3D-like vector for similarity search. It supports para' in text, "expected to find: " + 'Uploads multiple vector-embedded points to a Qdrant collection using the Python qdrant_client (PointStruct) with id, payload (e.g., color), and a 3D-like vector for similarity search. It supports para'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-clients-sdk/SKILL.md')
    assert 'curl -X GET "https://snippets.qdrant.tech/search?language=python&query=how+to+upload+points"' in text, "expected to find: " + 'curl -X GET "https://snippets.qdrant.tech/search?language=python&query=how+to+upload+points"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-clients-sdk/SKILL.md')
    assert 'If snippet output is required in json format, you can add `&format=json` to the query string' in text, "expected to find: " + 'If snippet output is required in json format, you can add `&format=json` to the query string'[:80]


"""Behavioral checks for llphant-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/llphant")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'docker compose exec php vendor/bin/pest tests/Integration/Embeddings/VectorStores/OpenSearch/OpenSearchVectorStoreTest.php' in text, "expected to find: " + 'docker compose exec php vendor/bin/pest tests/Integration/Embeddings/VectorStores/OpenSearch/OpenSearchVectorStoreTest.php'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Tests are written with Pest. There are two types of tests: unit tests, and integration tests. CI pipelines run only unit' in text, "expected to find: " + 'Tests are written with Pest. There are two types of tests: unit tests, and integration tests. CI pipelines run only unit'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The development environment is based on [docker-compose](docker/docker-compose.yml). Assume that no PHP interpreter is' in text, "expected to find: " + 'The development environment is based on [docker-compose](docker/docker-compose.yml). Assume that no PHP interpreter is'[:80]


"""Behavioral checks for elasticsearch-create-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/elasticsearch")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- For changes to a `Writeable` implementation (`writeTo` and constructor from `StreamInput`), add a new `public static final <UNIQUE_DESCRIPTIVE_NAME> = TransportVersion.fromName("<unique_descriptive_' in text, "expected to find: " + '- For changes to a `Writeable` implementation (`writeTo` and constructor from `StreamInput`), add a new `public static final <UNIQUE_DESCRIPTIVE_NAME> = TransportVersion.fromName("<unique_descriptive_'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use real classes over mocks or stubs for unit tests, unless the real class is complex then either a simplified subclass should be created within the test or, as a last resort, a mock or stub can be ' in text, "expected to find: " + '- Use real classes over mocks or stubs for unit tests, unless the real class is complex then either a simplified subclass should be created within the test or, as a last resort, a mock or stub can be '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Elasticsearch should prefer its own logger `org.elasticsearch.logging.LogManager` & `org.elasticsearch.logging.Logger`; declare `private static final Logger logger = LogManager.getLogger(Class.class' in text, "expected to find: " + '- Elasticsearch should prefer its own logger `org.elasticsearch.logging.LogManager` & `org.elasticsearch.logging.Logger`; declare `private static final Logger logger = LogManager.getLogger(Class.class'[:80]


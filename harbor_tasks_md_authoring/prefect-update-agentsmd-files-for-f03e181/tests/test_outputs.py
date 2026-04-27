"""Behavioral checks for prefect-update-agentsmd-files-for-f03e181 (markdown_authoring task).

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
    text = _read('src/prefect/AGENTS.md')
    assert '- `blocks/` → Server-persisted configuration objects for external service credentials and settings (see blocks/AGENTS.md)' in text, "expected to find: " + '- `blocks/` → Server-persisted configuration objects for external service credentials and settings (see blocks/AGENTS.md)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/blocks/AGENTS.md')
    assert '- **`position` in JSON schema** — `model_json_schema()` injects a `position` key (0-based field declaration order) into every property, including nested block definitions. This key affects the schema ' in text, "expected to find: " + '- **`position` in JSON schema** — `model_json_schema()` injects a `position` key (0-based field declaration order) into every property, including nested block definitions. This key affects the schema '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/blocks/AGENTS.md')
    assert 'Blocks handle configuration lifecycle: define fields in Python, register schema with the server, save/load named instances, and serialize secrets safely. They do NOT execute workflow logic — that belo' in text, "expected to find: " + 'Blocks handle configuration lifecycle: define fields in Python, register schema with the server, save/load named instances, and serialize secrets safely. They do NOT execute workflow logic — that belo'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/blocks/AGENTS.md')
    assert '- **Secret fields use dot-notation paths** — `"credentials.api_key"` means a nested field is secret; `"passwords.*"` means all values under that key are secret. The `secret_fields` list in the schema ' in text, "expected to find: " + '- **Secret fields use dot-notation paths** — `"credentials.api_key"` means a nested field is secret; `"passwords.*"` means all values under that key are secret. The `secret_fields` list in the schema '[:80]


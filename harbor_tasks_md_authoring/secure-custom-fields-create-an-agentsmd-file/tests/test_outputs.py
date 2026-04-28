"""Behavioral checks for secure-custom-fields-create-an-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/secure-custom-fields")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Naming**: New functions use `scf_` prefix and hooks use `scf/hook_name`, existing use `acf_` and `acf/hook_name` (backward compat)' in text, "expected to find: " + '- **Naming**: New functions use `scf_` prefix and hooks use `scf/hook_name`, existing use `acf_` and `acf/hook_name` (backward compat)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Internationalization**: Use `__()`, `_e()` with text domain `'secure-custom-fields'`" in text, "expected to find: " + "- **Internationalization**: Use `__()`, `_e()` with text domain `'secure-custom-fields'`"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Output escaping**: Always escape with `esc_html()`, `esc_attr()`, `esc_url()`' in text, "expected to find: " + '- **Output escaping**: Always escape with `esc_html()`, `esc_attr()`, `esc_url()`'[:80]


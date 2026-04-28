"""Behavioral checks for apple-browsers-cursor-rules-for-pixel-registry (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/apple-browsers")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pixel-definitions.mdc')
    assert 'A suffix is a string appended to the base pixel name to create distinct variants of the same pixel. For example, a pixel with the `"daily"` suffix set will produce a variant with `_daily` appended to ' in text, "expected to find: " + 'A suffix is a string appended to the base pixel name to create distinct variants of the same pixel. For example, a pixel with the `"daily"` suffix set will produce a variant with `_daily` appended to '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pixel-definitions.mdc')
    assert 'In some cases a suffix value is always present (rather than being a set of variants). For example, a pixel fired with the legacy daily frequency always gets `_d` appended to its name. When the suffix ' in text, "expected to find: " + 'In some cases a suffix value is always present (rather than being a set of variants). For example, a pixel fired with the legacy daily frequency always gets `_d` appended to its name. When the suffix '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pixel-definitions.mdc')
    assert "Check the pixel event's `parameters` computed property in Swift for any additional parameters. Also inspect the call site where the pixel is fired — look for `withAdditionalParameters:` arguments and " in text, "expected to find: " + "Check the pixel event's `parameters` computed property in Swift for any additional parameters. Also inspect the call site where the pixel is fired — look for `withAdditionalParameters:` arguments and "[:80]


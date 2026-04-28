"""Behavioral checks for uniwind-docs-update-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/uniwind")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/uniwind/SKILL.md')
    assert '**Supported group parents**: `Pressable` (press + focus), `Text` (press — requires `onPress`, even empty). `TouchableOpacity`, `TouchableHighlight`, `TouchableWithoutFeedback`, and `TextInput` do **no' in text, "expected to find: " + '**Supported group parents**: `Pressable` (press + focus), `Text` (press — requires `onPress`, even empty). `TouchableOpacity`, `TouchableHighlight`, `TouchableWithoutFeedback`, and `TextInput` do **no'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/uniwind/SKILL.md')
    assert '**Not supported**: `group-hover:*` (no pointer hover on native), `group-disabled:*` (parsed but no shadow tree trigger), arbitrary `group-[.selector]:*` variants, implicit `in-*` variants.' in text, "expected to find: " + '**Not supported**: `group-hover:*` (no pointer hover on native), `group-disabled:*` (parsed but no shadow tree trigger), arbitrary `group-[.selector]:*` variants, implicit `in-*` variants.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/uniwind/SKILL.md')
    assert '- **Group variants**: Tailwind `group-active:*` / `group-focus:*` propagate parent interaction state through the C++ shadow tree with zero re-renders' in text, "expected to find: " + '- **Group variants**: Tailwind `group-active:*` / `group-focus:*` propagate parent interaction state through the C++ shadow tree with zero re-renders'[:80]


"""Behavioral checks for rmk-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rmk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test-changes/SKILL.md')
    assert '.claude/skills/test-changes/SKILL.md' in text, "expected to find: " + '.claude/skills/test-changes/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'RMK is a Rust keyboard firmware library targeting embedded microcontrollers (`no_std` by default). It supports USB and BLE keyboards, split keyboards, on-the-fly keymap configuration(Vial), and advanc' in text, "expected to find: " + 'RMK is a Rust keyboard firmware library targeting embedded microcontrollers (`no_std` by default). It supports USB and BLE keyboards, split keyboards, on-the-fly keymap configuration(Vial), and advanc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`keyboard.toml` is parsed by `rmk-config` (`KeyboardTomlConfig`) at two points: by `rmk/build.rs` at build time, and by `rmk-macro` at macro-expansion time. The path defaults to `keyboard.toml` next t' in text, "expected to find: " + '`keyboard.toml` is parsed by `rmk-config` (`KeyboardTomlConfig`) at two points: by `rmk/build.rs` at build time, and by `rmk-macro` at macro-expansion time. The path defaults to `keyboard.toml` next t'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`build.rs` reads only the `[rmk]` and `[event]` sections, then emits `constants.rs` as Rust `const` items. The full `KeyboardTomlConfig` struct in `rmk-config/src/lib.rs` is the authoritative referenc' in text, "expected to find: " + '`build.rs` reads only the `[rmk]` and `[event]` sections, then emits `constants.rs` as Rust `const` items. The full `KeyboardTomlConfig` struct in `rmk-config/src/lib.rs` is the authoritative referenc'[:80]


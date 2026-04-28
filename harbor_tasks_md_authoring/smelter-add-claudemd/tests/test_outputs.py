"""Behavioral checks for smelter-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/smelter")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'Smelter is a toolkit for real-time, low-latency, programmable video and audio composition. It combines multimedia from different sources into a single video or live stream, with support for text, cust' in text, "expected to find: " + 'Smelter is a toolkit for real-time, low-latency, programmable video and audio composition. It combines multimedia from different sources into a single video or live stream, with support for text, cust'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- **`smelter-render`** — GPU rendering engine (wgpu). Takes input frames → produces composed output frames. Handles YUV/NV12↔RGBA conversion, scene layout, animations/transitions. Two core entrypoints' in text, "expected to find: " + '- **`smelter-render`** — GPU rendering engine (wgpu). Takes input frames → produces composed output frames. Handles YUV/NV12↔RGBA conversion, scene layout, animations/transitions. Two core entrypoints'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- **`smelter-core`** — Main library. Pipeline management, queue logic, encoding/decoding, muxing/transport protocols, audio mixing. Uses `smelter-render` for composition.' in text, "expected to find: " + '- **`smelter-core`** — Main library. Pipeline management, queue logic, encoding/decoding, muxing/transport protocols, audio mixing. Uses `smelter-render` for composition.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/api-change/SKILL.md')
    assert '- add/modify mapping in `ts/smelter-core` package e.g. `ts/smelter-core/src/api/input.ts`. In most cases it will be just switching snake case to camel case, but consider if there are more idiomatic al' in text, "expected to find: " + '- add/modify mapping in `ts/smelter-core` package e.g. `ts/smelter-core/src/api/input.ts`. In most cases it will be just switching snake case to camel case, but consider if there are more idiomatic al'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/api-change/SKILL.md')
    assert 'description: Run the full API change workflow after modifying types in smelter-api. Generates schemas, TypeScript types, and verifies everything is in sync.' in text, "expected to find: " + 'description: Run the full API change workflow after modifying types in smelter-api. Generates schemas, TypeScript types, and verifies everything is in sync.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/api-change/SKILL.md')
    assert '4. **Show a summary of all generated/changed files** so the user can review what was affected.' in text, "expected to find: " + '4. **Show a summary of all generated/changed files** so the user can review what was affected.'[:80]


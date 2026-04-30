"""Behavioral checks for tilelang-add-agentsskillsbuildskillmd-for-build-conventions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tilelang")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/build/SKILL.md')
    assert '**Never use `pip install -e .`** (editable install). When running Python from the repo root, the local `./tilelang` directory is imported instead of the installed copy (because `.` is on `sys.path` by' in text, "expected to find: " + '**Never use `pip install -e .`** (editable install). When running Python from the repo root, the local `./tilelang` directory is imported instead of the installed copy (because `.` is on `sys.path` by'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/build/SKILL.md')
    assert 'After the initial configure, recompiling is just `cmake --build build -j$(nproc)`. The runtime automatically discovers native libraries from `build/lib/` when it detects a dev checkout (see `tilelang/' in text, "expected to find: " + 'After the initial configure, recompiling is just `cmake --build build -j$(nproc)`. The runtime automatically discovers native libraries from `build/lib/` when it detects a dev checkout (see `tilelang/'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/build/SKILL.md')
    assert 'If you need faster iteration (e.g. calling `cmake` directly to recompile C++ without re-running the full pip install), install build dependencies first:' in text, "expected to find: " + 'If you need faster iteration (e.g. calling `cmake` directly to recompile C++ without re-running the full pip install), install build dependencies first:'[:80]


"""Behavioral checks for skills-docsaflpp-add-opinionated-environment-variables (markdown_authoring task).

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
    text = _read('plugins/testing-handbook-skills/skills/aflpp/SKILL.md')
    assert '`AFL_FINAL_SYNC` tells the primary instance to do a final import from all secondaries when stopping. This does not affect the fuzzing process itself — it only matters when you later run `afl-cmin` for' in text, "expected to find: " + '`AFL_FINAL_SYNC` tells the primary instance to do a final import from all secondaries when stopping. This does not affect the fuzzing process itself — it only matters when you later run `afl-cmin` for'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/testing-handbook-skills/skills/aflpp/SKILL.md')
    assert '`AFL_FAST_CAL` reduces calibration time with negligible precision loss. Recommended specifically for slow targets where calibration would otherwise take a long time.' in text, "expected to find: " + '`AFL_FAST_CAL` reduces calibration time with negligible precision loss. Recommended specifically for slow targets where calibration would otherwise take a long time.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/testing-handbook-skills/skills/aflpp/SKILL.md')
    assert 'AFL++ has [many environment variables](https://aflplus.plus/docs/env_variables/), but most are niche. These are the ones that matter in practice.' in text, "expected to find: " + 'AFL++ has [many environment variables](https://aflplus.plus/docs/env_variables/), but most are niche. These are the ones that matter in practice.'[:80]


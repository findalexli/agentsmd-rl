"""Behavioral checks for runtime-improve-performancebenchmarkskillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/runtime")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/performance-benchmark/SKILL.md')
    assert '- **Check the manual**: EgorBot replies include a link to the [manual](https://github.com/EgorBo/EgorBot?tab=readme-ov-file#github-usage) for advanced options' in text, "expected to find: " + '- **Check the manual**: EgorBot replies include a link to the [manual](https://github.com/EgorBo/EgorBot?tab=readme-ov-file#github-usage) for advanced options'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/performance-benchmark/SKILL.md')
    assert 'When you need to validate the performance impact of a code change, follow this process to write a BenchmarkDotNet benchmark and trigger @EgorBot to run it.' in text, "expected to find: " + 'When you need to validate the performance impact of a code change, follow this process to write a BenchmarkDotNet benchmark and trigger @EgorBot to run it.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/performance-benchmark/SKILL.md')
    assert 'Use `-profiler` when absolutely necessary along with `-linux_arm64` and/or `-linux_amd` to include `perf` profiling and disassembly in the results.' in text, "expected to find: " + 'Use `-profiler` when absolutely necessary along with `-linux_arm64` and/or `-linux_amd` to include `perf` profiling and disassembly in the results.'[:80]


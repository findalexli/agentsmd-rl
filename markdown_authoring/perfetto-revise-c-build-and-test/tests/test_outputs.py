"""Behavioral checks for perfetto-revise-c-build-and-test (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/perfetto")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Other target names are usually: traced, traced_probes, perfetto, trace_processor_shell. You can discover them following the root /BUILD.gn file' in text, "expected to find: " + '- Other target names are usually: traced, traced_probes, perfetto, trace_processor_shell. You can discover them following the root /BUILD.gn file'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'tools/diff_test_trace_processor.py $OUT$/trace_processor_shell --keep-input --quiet --name-filter="<regex of test names>"' in text, "expected to find: " + 'tools/diff_test_trace_processor.py $OUT$/trace_processor_shell --keep-input --quiet --name-filter="<regex of test names>"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Usually there is a BUILD.gn file in each directory. If not, look at closer parent dirs for precedent.' in text, "expected to find: " + 'Usually there is a BUILD.gn file in each directory. If not, look at closer parent dirs for precedent.'[:80]


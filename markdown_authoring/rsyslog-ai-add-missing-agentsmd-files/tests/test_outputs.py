"""Behavioral checks for rsyslog-ai-add-missing-agentsmd-files (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rsyslog")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('runtime/AGENTS.md')
    assert '- `parser.c`, `prop.c`, `template.c`: core message parsing and property engine.' in text, "expected to find: " + '- `parser.c`, `prop.c`, `template.c`: core message parsing and property engine.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('runtime/AGENTS.md')
    assert '- Follow `COMMENTING_STYLE.md` and add/update "Concurrency & Locking" blocks in' in text, "expected to find: " + '- Follow `COMMENTING_STYLE.md` and add/update "Concurrency & Locking" blocks in'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('runtime/AGENTS.md')
    assert '- Keep worker/thread behavior aligned with `MODULE_AUTHOR_CHECKLIST.md` rules:' in text, "expected to find: " + '- Keep worker/thread behavior aligned with `MODULE_AUTHOR_CHECKLIST.md` rules:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('tests/AGENTS.md')
    assert '- Base new shell tests on existing ones; include `. $srcdir/diag.sh` to gain the' in text, "expected to find: " + '- Base new shell tests on existing ones; include `. $srcdir/diag.sh` to gain the'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('tests/AGENTS.md')
    assert '- Name Valgrind-enabled wrappers with the `-vg.sh` suffix and toggle Valgrind by' in text, "expected to find: " + '- Name Valgrind-enabled wrappers with the `-vg.sh` suffix and toggle Valgrind by'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('tests/AGENTS.md')
    assert '- Put auxiliary binaries next to their scripts (e.g. `*.c` programs compiled via' in text, "expected to find: " + '- Put auxiliary binaries next to their scripts (e.g. `*.c` programs compiled via'[:80]


"""Behavioral checks for htcondor-htcondor3631-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/htcondor")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Debug Categories:** For daemons, enable fine-grained logging via `ALL_DEBUG`, `DEFAULT_DEBUG`, and `<SUBSYS>_DEBUG` config parameters; for command-line tools, use `TOOL_DEBUG`. Common categories: `D' in text, "expected to find: " + '**Debug Categories:** For daemons, enable fine-grained logging via `ALL_DEBUG`, `DEFAULT_DEBUG`, and `<SUBSYS>_DEBUG` config parameters; for command-line tools, use `TOOL_DEBUG`. Common categories: `D'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'HTCondor is a **distributed high-throughput computing system** written in C++20. The codebase consists of multiple daemons communicating via ClassAd messages over network sockets to schedule and execu' in text, "expected to find: " + 'HTCondor is a **distributed high-throughput computing system** written in C++20. The codebase consists of multiple daemons communicating via ClassAd messages over network sockets to schedule and execu'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Golden Rule**: In daemon code, ALWAYS use DaemonCore for timers/signals/sockets. Never use raw POSIX calls (`timer_create()`, `signal()`, etc.) as they bypass the event loop.' in text, "expected to find: " + '**Golden Rule**: In daemon code, ALWAYS use DaemonCore for timers/signals/sockets. Never use raw POSIX calls (`timer_create()`, `signal()`, etc.) as they bypass the event loop.'[:80]


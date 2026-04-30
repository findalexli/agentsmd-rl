"""Behavioral checks for kscrash-add-asyncsignalsafetyreview-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kscrash")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/async-signal-safety-review/SKILL.md')
    assert 'description: Review code changes for async-signal-safety violations in KSCrash crash handlers, signal handlers, and monitor code. Verifies suspect system calls by reading the actual implementation in ' in text, "expected to find: " + 'description: Review code changes for async-signal-safety violations in KSCrash crash handlers, signal handlers, and monitor code. Verifies suspect system calls by reading the actual implementation in '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/async-signal-safety-review/SKILL.md')
    assert 'For each signal-reachable function, follow **every call it makes** — including into other files, other modules, and system libraries. A function that looks clean itself but calls a helper in `KSString' in text, "expected to find: " + 'For each signal-reachable function, follow **every call it makes** — including into other files, other modules, and system libraries. A function that looks clean itself but calls a helper in `KSString'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/async-signal-safety-review/SKILL.md')
    assert 'Not every function in a file needs signal-safety. First, determine which functions are on the **critical path** — reachable (directly or transitively) from a signal/crash handler. Entry points to trac' in text, "expected to find: " + 'Not every function in a file needs signal-safety. First, determine which functions are on the **critical path** — reachable (directly or transitively) from a signal/crash handler. Entry points to trac'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/async-signal-safety-review/apple-oss-reference.md')
    assert "> Verify whether `strerror_r` is async-signal-safe on Apple. It's in apple-oss-distributions/Libc. Fetch the implementation (try `gen/FreeBSD/strerror.c` first via `gh api repos/apple-oss-distribution" in text, "expected to find: " + "> Verify whether `strerror_r` is async-signal-safe on Apple. It's in apple-oss-distributions/Libc. Fetch the implementation (try `gen/FreeBSD/strerror.c` first via `gh api repos/apple-oss-distribution"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/async-signal-safety-review/apple-oss-reference.md')
    assert "If `gh` isn't available or the path is already known, use WebFetch against the `raw.githubusercontent.com` URL for the repo's default branch (usually `main`). Example: `https://raw.githubusercontent.c" in text, "expected to find: " + "If `gh` isn't available or the path is already known, use WebFetch against the `raw.githubusercontent.com` URL for the repo's default branch (usually `main`). Example: `https://raw.githubusercontent.c"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/async-signal-safety-review/apple-oss-reference.md')
    assert 'Each "is function X actually async-signal-safe on Apple?" lookup is **independent** and **context-heavy** (you may have to read several files to trace helpers). Do not do them inline in the main conve' in text, "expected to find: " + 'Each "is function X actually async-signal-safe on Apple?" lookup is **independent** and **context-heavy** (you may have to read several files to trace helpers). Do not do them inline in the main conve'[:80]


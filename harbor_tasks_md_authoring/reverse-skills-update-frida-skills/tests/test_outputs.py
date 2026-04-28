"""Behavioral checks for reverse-skills-update-frida-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/reverse-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rev-frida/SKILL.md')
    assert 'description: Generate Frida hook scripts using modern Frida API. Activate when the user wants to write Frida scripts, hook functions at runtime, trace calls or arguments or return values, intercept na' in text, "expected to find: " + 'description: Generate Frida hook scripts using modern Frida API. Activate when the user wants to write Frida scripts, hook functions at runtime, trace calls or arguments or return values, intercept na'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rev-frida/SKILL.md')
    assert '- “The process dies during native library initialization. First hook the constructor dispatcher such as `call_constructors` or `call_array` if present, log the constructor targets, then move to the ex' in text, "expected to find: " + '- “The process dies during native library initialization. First hook the constructor dispatcher such as `call_constructors` or `call_array` if present, log the constructor targets, then move to the ex'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rev-frida/SKILL.md')
    assert 'If anti-debug logic is suspected inside the constructor chain, prefer observing or hooking the dispatcher first instead of attaching blindly to raw `.init_array` entries.' in text, "expected to find: " + 'If anti-debug logic is suspected inside the constructor chain, prefer observing or hooking the dispatcher first instead of attaching blindly to raw `.init_array` entries.'[:80]


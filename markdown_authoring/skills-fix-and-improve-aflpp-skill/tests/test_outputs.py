"""Behavioral checks for skills-fix-and-improve-aflpp-skill (markdown_authoring task).

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
    assert 'Refer to the [Dockerfile](https://github.com/AFLplusplus/AFLplusplus/blob/stable/Dockerfile) for Ubuntu version requirements and dependencies. Set `LLVM_CONFIG` to specify Clang version (e.g., `llvm-c' in text, "expected to find: " + 'Refer to the [Dockerfile](https://github.com/AFLplusplus/AFLplusplus/blob/stable/Dockerfile) for Ubuntu version requirements and dependencies. Set `LLVM_CONFIG` to specify Clang version (e.g., `llvm-c'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/testing-handbook-skills/skills/aflpp/SKILL.md')
    assert '| Use LLVMFuzzerTestOneInput harnesses where possible | If a fuzzing campaign has at least 85% stability then this is the most efficient fuzzing style. If not then try standard input or file input fuz' in text, "expected to find: " + '| Use LLVMFuzzerTestOneInput harnesses where possible | If a fuzzing campaign has at least 85% stability then this is the most efficient fuzzing style. If not then try standard input or file input fuz'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/testing-handbook-skills/skills/aflpp/SKILL.md')
    assert 'Prior to installing afl++, check the clang version dependency of the packge with `apt-cache show afl++`, and install the matching `lld` version (e.g., `lld-17`).' in text, "expected to find: " + 'Prior to installing afl++, check the clang version dependency of the packge with `apt-cache show afl++`, and install the matching `lld` version (e.g., `lld-17`).'[:80]


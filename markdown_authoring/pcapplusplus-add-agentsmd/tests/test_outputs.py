"""Behavioral checks for pcapplusplus-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pcapplusplus")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Formatting:** Use `clang-format` version 19.1.6 (could be installed in Python via virtualenv). A `.clang-format` is present at the repository root. Format new code' in text, "expected to find: " + '- **Formatting:** Use `clang-format` version 19.1.6 (could be installed in Python via virtualenv). A `.clang-format` is present at the repository root. Format new code'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '4. Register the protocol in `parseNextLayer()` of the previous protocol (that could be `TcpLayer`, `UdpLayer`, `EthLayer`, etc., or sometimes multiple protocols)' in text, "expected to find: " + '4. Register the protocol in `parseNextLayer()` of the previous protocol (that could be `TcpLayer`, `UdpLayer`, `EthLayer`, etc., or sometimes multiple protocols)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Register new tests in the `TestDefinition.h` and add `PTF_RUN_TEST(<TEST_NAME>)` in `main.cpp`, assigning meaningful tags.' in text, "expected to find: " + '- Register new tests in the `TestDefinition.h` and add `PTF_RUN_TEST(<TEST_NAME>)` in `main.cpp`, assigning meaningful tags.'[:80]


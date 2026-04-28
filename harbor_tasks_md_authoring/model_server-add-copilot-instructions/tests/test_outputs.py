"""Behavioral checks for model_server-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/model-server")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'OpenVINO Model Server (OVMS) is a high-performance inference serving platform built on top of **OpenVINO** and **OpenVINO GenAI**. The codebase is primarily **C++** with **Bazel** as the build system.' in text, "expected to find: " + 'OpenVINO Model Server (OVMS) is a high-performance inference serving platform built on top of **OpenVINO** and **OpenVINO GenAI**. The codebase is primarily **C++** with **Bazel** as the build system.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Forward-declare in headers, include in `.cpp`**: if a header only uses pointers or references to a type, use a forward declaration (`class Foo;`) instead of `#include "foo.hpp"`. Move the full `#i' in text, "expected to find: " + '- **Forward-declare in headers, include in `.cpp`**: if a header only uses pointers or references to a type, use a forward declaration (`class Foo;`) instead of `#include "foo.hpp"`. Move the full `#i'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Performance is a top priority** — both **throughput** and **latency** are critical. Code changes should be evaluated for their performance impact. Avoid unnecessary copies, allocations, and blocking' in text, "expected to find: " + '**Performance is a top priority** — both **throughput** and **latency** are critical. Code changes should be evaluated for their performance impact. Avoid unnecessary copies, allocations, and blocking'[:80]


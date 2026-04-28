"""Behavioral checks for jint-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jint")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. For JS script file benchmarks, extend `SingleScriptBenchmark` and override `FileName` to point at a file in `Scripts/`. The base class handles loading, parsing (`Engine.PrepareScript`), and provide' in text, "expected to find: " + '2. For JS script file benchmarks, extend `SingleScriptBenchmark` and override `FileName` to point at a file in `Scripts/`. The base class handles loading, parsing (`Engine.PrepareScript`), and provide'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `Jint.Native` — JS value types and built-in objects. Each built-in has a subdirectory with `*Constructor`, `*Prototype`, `*Instance` classes (e.g., `Native/Array/ArrayConstructor.cs`, `ArrayPrototyp' in text, "expected to find: " + '- `Jint.Native` — JS value types and built-in objects. Each built-in has a subdirectory with `*Constructor`, `*Prototype`, `*Instance` classes (e.g., `Native/Array/ArrayConstructor.cs`, `ArrayPrototyp'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`Jint.Tests`** — Main unit tests. Test classes mirror runtime types (e.g., `EngineTests`, `InteropTests`, `ArrayTests`). JS test scripts are embedded resources in `Runtime/Scripts/` and `Parser/Sc' in text, "expected to find: " + '- **`Jint.Tests`** — Main unit tests. Test classes mirror runtime types (e.g., `EngineTests`, `InteropTests`, `ArrayTests`). JS test scripts are embedded resources in `Runtime/Scripts/` and `Parser/Sc'[:80]


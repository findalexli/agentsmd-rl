"""Behavioral checks for aztec-packages-featavm-claude-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aztec-packages")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('barretenberg/cpp/CLAUDE.md')
    assert '- **vm2/** - AVM implementation (not enabled, but might need to be fixed for compilation issues in root ./bootstrap.sh). If working in vm2, use barretenberg/cpp/src/barretenberg/vm2/CLAUDE.md' in text, "expected to find: " + '- **vm2/** - AVM implementation (not enabled, but might need to be fixed for compilation issues in root ./bootstrap.sh). If working in vm2, use barretenberg/cpp/src/barretenberg/vm2/CLAUDE.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('barretenberg/cpp/pil/vm2/CLAUDE.md')
    assert 'The **Aztec Virtual Machine (AVM)** executes public transactions and proves correct execution. The **PIL files** in this directory define **relations**: constraints on a trace (matrix of columns and r' in text, "expected to find: " + 'The **Aztec Virtual Machine (AVM)** executes public transactions and proves correct execution. The **PIL files** in this directory define **relations**: constraints on a trace (matrix of columns and r'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('barretenberg/cpp/pil/vm2/CLAUDE.md')
    assert '**Scope:** Use this guide when editing PIL relation files in `barretenberg/cpp/pil/vm2`. After changing PIL you must regenerate C++ and recompile; the C++ side is in `barretenberg/cpp/src/barretenberg' in text, "expected to find: " + '**Scope:** Use this guide when editing PIL relation files in `barretenberg/cpp/pil/vm2`. After changing PIL you must regenerate C++ and recompile; the C++ side is in `barretenberg/cpp/src/barretenberg'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('barretenberg/cpp/pil/vm2/CLAUDE.md')
    assert '1. **Ensure `bb-pilcom` is built** (once per checkout / when pilcom changes). From repo root: run `./bootstrap.sh` in `bb-pilcom/` (e.g. `bb-pilcom/bootstrap.sh`). Changes to PIL do not require rebuil' in text, "expected to find: " + '1. **Ensure `bb-pilcom` is built** (once per checkout / when pilcom changes). From repo root: run `./bootstrap.sh` in `bb-pilcom/` (e.g. `bb-pilcom/bootstrap.sh`). Changes to PIL do not require rebuil'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('barretenberg/cpp/src/barretenberg/vm2/CLAUDE.md')
    assert '**Scope:** Use this guide when working in `barretenberg/cpp/src/barretenberg/vm2` — the AVM C++ simulator, trace generation, and prover. For barretenberg-wide build and workflow, see `barretenberg/cpp' in text, "expected to find: " + '**Scope:** Use this guide when working in `barretenberg/cpp/src/barretenberg/vm2` — the AVM C++ simulator, trace generation, and prover. For barretenberg-wide build and workflow, see `barretenberg/cpp'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('barretenberg/cpp/src/barretenberg/vm2/CLAUDE.md')
    assert '- Build: `cmake --build --preset clang20-assert --target nodejs_module`. For TS: from `barretenberg/cpp/`, run `(cd ../../barretenberg/ts/; ./scripts/copy_native.sh)` then bootstrap `yarn-project` (se' in text, "expected to find: " + '- Build: `cmake --build --preset clang20-assert --target nodejs_module`. For TS: from `barretenberg/cpp/`, run `(cd ../../barretenberg/ts/; ./scripts/copy_native.sh)` then bootstrap `yarn-project` (se'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('barretenberg/cpp/src/barretenberg/vm2/CLAUDE.md')
    assert 'Most end-to-end AVM behavior is tested from TypeScript. Ensure `yarn-project` is bootstrapped (see yarn-project/CLAUDE.md); rebuild only if the repo or TS files changed.' in text, "expected to find: " + 'Most end-to-end AVM behavior is tested from TypeScript. Ensure `yarn-project` is bootstrapped (see yarn-project/CLAUDE.md); rebuild only if the repo or TS files changed.'[:80]


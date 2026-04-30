"""Behavioral checks for daft-docsskills-add-claude-code-compatible (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/daft")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daft-distributed-scaling/SKILL.md')
    assert '| **Streaming** | `into_batches(N)` | Heavy data (images, tensors) | **Low memory** (streaming). High scheduling overhead if batches too small. |' in text, "expected to find: " + '| **Streaming** | `into_batches(N)` | Heavy data (images, tensors) | **Low memory** (streaming). High scheduling overhead if batches too small. |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daft-distributed-scaling/SKILL.md')
    assert '| **Shuffle** | `repartition(N)` | Light data (e.g. file paths), Joins | **Global balance**. High memory usage (materializes data). |' in text, "expected to find: " + '| **Shuffle** | `repartition(N)` | Light data (e.g. file paths), Joins | **Global balance**. High memory usage (materializes data). |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daft-distributed-scaling/SKILL.md')
    assert 'description: "Scale Daft workflows to distributed Ray clusters. Invoke when optimizing performance or handling large data."' in text, "expected to find: " + 'description: "Scale Daft workflows to distributed Ray clusters. Invoke when optimizing performance or handling large data."'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daft-docs-navigation/SKILL.md')
    assert 'description: "Navigate Daft documentation. Invoke when user asks general questions about APIs, concepts, or examples, or wants to search the docs."' in text, "expected to find: " + 'description: "Navigate Daft documentation. Invoke when user asks general questions about APIs, concepts, or examples, or wants to search the docs."'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daft-docs-navigation/SKILL.md')
    assert '-   If `docs/` is missing or empty, clone the repo: `git clone https://github.com/Eventual-Inc/Daft.git`' in text, "expected to find: " + '-   If `docs/` is missing or empty, clone the repo: `git clone https://github.com/Eventual-Inc/Daft.git`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daft-docs-navigation/SKILL.md')
    assert '1.  **Live Site**: [`https://docs.daft.ai`](https://docs.daft.ai) (Primary source, searchable).' in text, "expected to find: " + '1.  **Live Site**: [`https://docs.daft.ai`](https://docs.daft.ai) (Primary source, searchable).'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daft-udf-tuning/SKILL.md')
    assert 'description: "Optimize Daft UDF performance. Invoke when user needs GPU inference, encounters slow UDFs, or asks about async/batch processing."' in text, "expected to find: " + 'description: "Optimize Daft UDF performance. Invoke when user needs GPU inference, encounters slow UDFs, or asks about async/batch processing."'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daft-udf-tuning/SKILL.md')
    assert '| **Stateful** | `@daft.cls` | Expensive init (e.g., loading models). Supports `gpus=N`. |' in text, "expected to find: " + '| **Stateful** | `@daft.cls` | Expensive init (e.g., loading models). Supports `gpus=N`. |'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/daft-udf-tuning/SKILL.md')
    assert '| **Stateless** | `@daft.func` | Simple transforms. Use `async` for I/O-bound tasks. |' in text, "expected to find: " + '| **Stateless** | `@daft.func` | Simple transforms. Use `async` for I/O-bound tasks. |'[:80]


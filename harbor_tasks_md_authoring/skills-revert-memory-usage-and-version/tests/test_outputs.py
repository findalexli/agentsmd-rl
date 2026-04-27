"""Behavioral checks for skills-revert-memory-usage-and-version (markdown_authoring task).

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
    text = _read('skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md')
    assert '- For low RAM environments, consider `async_scorer` config, which enables support of `io_uring` for parallel disk access, which can significantly improve performance of on-disk storage. Read more abou' in text, "expected to find: " + '- For low RAM environments, consider `async_scorer` config, which enables support of `io_uring` for parallel disk access, which can significantly improve performance of on-disk storage. Read more abou'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md')
    assert '- Leverage Matryoshka Representation Learning (MRL) to store only small vectors in RAM, while keeping large vectors on disk. Examples of how to use MRL with qdrant cloud inference: [MRL docs](https://' in text, "expected to find: " + '- Leverage Matryoshka Representation Learning (MRL) to store only small vectors in RAM, while keeping large vectors on disk. Examples of how to use MRL with qdrant cloud inference: [MRL docs](https://'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md')
    assert '- For deployments with fast local storage and relatively low requirements for search throughput, it may be possible to store all components of vector store on disk. Read more about the performance imp' in text, "expected to find: " + '- For deployments with fast local storage and relatively low requirements for search throughput, it may be possible to store all components of vector store on disk. Read more about the performance imp'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-version-upgrade/SKILL.md')
    assert '- Storage compatibility is only guaranteed for one minor version. For example, data stored with Qdrant 1.16.x is expected to be compatible with Qdrant 1.17.x. If you need to migrate more than 1 minor ' in text, "expected to find: " + '- Storage compatibility is only guaranteed for one minor version. For example, data stored with Qdrant 1.16.x is expected to be compatible with Qdrant 1.17.x. If you need to migrate more than 1 minor '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-version-upgrade/SKILL.md')
    assert '- Qdrant cluster with replication factor of 2 and above can be upgraded without downtime, by performing a rolling upgrade. This means that you can upgrade one node at a time, while the other nodes con' in text, "expected to find: " + '- Qdrant cluster with replication factor of 2 and above can be upgraded without downtime, by performing a rolling upgrade. This means that you can upgrade one node at a time, while the other nodes con'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-version-upgrade/SKILL.md')
    assert '- Qdrant is tested for backward compatibility between minor versions. For example, Qdrant 1.17.x should be compatible with SDK 1.16.x. Qdrant server 1.16.x is also expected to be compatible with SDK 1' in text, "expected to find: " + '- Qdrant is tested for backward compatibility between minor versions. For example, Qdrant 1.17.x should be compatible with SDK 1.16.x. Qdrant server 1.16.x is also expected to be compatible with SDK 1'[:80]


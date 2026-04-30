"""Behavioral checks for oraxen-chore-fix-duplicated-content-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/oraxen")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/architecture.mdc')
    assert '- NMS version modules: `v1_20_R1` … `v1_21_R6`. Each implements NMS shims for a specific server version (e.g., `io.th0rgal.oraxen.nms.v1_21_R6.NMSHandler`). They are discovered at runtime via reflecti' in text, "expected to find: " + '- NMS version modules: `v1_20_R1` … `v1_21_R6`. Each implements NMS shims for a specific server version (e.g., `io.th0rgal.oraxen.nms.v1_21_R6.NMSHandler`). They are discovered at runtime via reflecti'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/architecture.mdc')
    assert "- Repositories: Paper, Spigot, Sonatype snapshots, JitPack, Oraxen's repos, etc." in text, "expected to find: " + "- Repositories: Paper, Spigot, Sonatype snapshots, JitPack, Oraxen's repos, etc."[:80]


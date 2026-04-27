"""Behavioral checks for cloudbase-mcp-docsguideline-trim-duplicated-cloudbase-guidan (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cloudbase-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/guideline/cloudbase/SKILL.md')
    assert 'The CloudBase console changes frequently. If a logged-in console shows a different hash path from this list, prefer the live console path and update the source guideline instead of copying stale URLs ' in text, "expected to find: " + 'The CloudBase console changes frequently. If a logged-in console shows a different hash path from this list, prefer the live console path and update the source guideline instead of copying stale URLs '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/guideline/cloudbase/SKILL.md')
    assert 'After creating or deploying resources, provide the corresponding console management link. All console URLs follow the pattern: `https://tcb.cloud.tencent.com/dev?envId=${envId}#/{path}`.' in text, "expected to find: " + 'After creating or deploying resources, provide the corresponding console management link. All console URLs follow the pattern: `https://tcb.cloud.tencent.com/dev?envId=${envId}#/{path}`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/guideline/cloudbase/SKILL.md')
    assert '- **Document Database (文档型数据库)**: `#/db/doc` - Collections: `#/db/doc/collection/${collectionName}`, Models: `#/db/doc/model/${modelName}`' in text, "expected to find: " + '- **Document Database (文档型数据库)**: `#/db/doc` - Collections: `#/db/doc/collection/${collectionName}`, Models: `#/db/doc/model/${modelName}`'[:80]


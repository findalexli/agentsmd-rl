"""Behavioral checks for ant-design-choreskills-improve-createpr-skill-trigger (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ant-design")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-pr/SKILL.md')
    assert '- 英文：`create pr`、`create a pr`、`open pr`、`open a pr`、`submit pr`、`send pr`、`draft pr`、`prepare pr`、`help me create a pr`、`open a pull request`。' in text, "expected to find: " + '- 英文：`create pr`、`create a pr`、`open pr`、`open a pr`、`submit pr`、`send pr`、`draft pr`、`prepare pr`、`help me create a pr`、`open a pull request`。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-pr/SKILL.md')
    assert '- 中文：`创建pr`、`创建 PR`、`开pr`、`开个pr`、`提pr`、`提个pr`、`帮我提个pr`、`发pr`、`写pr`、`准备pr`。' in text, "expected to find: " + '- 中文：`创建pr`、`创建 PR`、`开pr`、`开个pr`、`提pr`、`提个pr`、`帮我提个pr`、`发pr`、`写pr`、`准备pr`。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-pr/SKILL.md')
    assert '这类短句默认表示：先分析当前分支改动并整理待确认的 `base`、`title`、`body` 草稿，等用户确认后再真正创建 PR。' in text, "expected to find: " + '这类短句默认表示：先分析当前分支改动并整理待确认的 `base`、`title`、`body` 草稿，等用户确认后再真正创建 PR。'[:80]


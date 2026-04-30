"""Behavioral checks for ant-design-docs-refine-createpr-trigger-guidance (markdown_authoring task).

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
    assert "description: Create pull requests for ant-design using the repository's official PR templates. Use this skill when the user asks to create/open a PR, draft PR title/body, summarize branch changes for " in text, "expected to find: " + "description: Create pull requests for ant-design using the repository's official PR templates. Use this skill when the user asks to create/open a PR, draft PR title/body, summarize branch changes for "[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-pr/SKILL.md')
    assert '不要把触发限制成固定说法。即使用户表达很短、很口语，或要求不完整，只要不是在单纯讨论 PR 概念，也应进入本 skill 的工作流。' in text, "expected to find: " + '不要把触发限制成固定说法。即使用户表达很短、很口语，或要求不完整，只要不是在单纯讨论 PR 概念，也应进入本 skill 的工作流。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-pr/SKILL.md')
    assert '只要能判断用户是在请求创建 PR，或为创建 PR 做准备，就应使用本 skill。' in text, "expected to find: " + '只要能判断用户是在请求创建 PR，或为创建 PR 做准备，就应使用本 skill。'[:80]


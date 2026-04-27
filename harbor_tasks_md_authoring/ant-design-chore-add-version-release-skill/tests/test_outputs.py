"""Behavioral checks for ant-design-chore-add-version-release-skill (markdown_authoring task).

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
    text = _read('.agents/skills/version-release/SKILL.md')
    assert 'description: ant-design 仓库的版本发布工作流。在用户提到发版、准备 release PR、升级发布版本号、执行正式 npm publish、或处理 release 分支与发布校验时使用。它不负责收集或生成 changelog；涉及 changelog 收集、整理、改写时应使用 changelog-collect。' in text, "expected to find: " + 'description: ant-design 仓库的版本发布工作流。在用户提到发版、准备 release PR、升级发布版本号、执行正式 npm publish、或处理 release 分支与发布校验时使用。它不负责收集或生成 changelog；涉及 changelog 收集、整理、改写时应使用 changelog-collect。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/version-release/SKILL.md')
    assert '`npm run version` 只在需要刷新本地生成的版本文件、做校验时才运行。不要把无关的生成文件顺手带进 release PR，除非仓库本来就预期它们会被更新。' in text, "expected to find: " + '`npm run version` 只在需要刷新本地生成的版本文件、做校验时才运行。不要把无关的生成文件顺手带进 release PR，除非仓库本来就预期它们会被更新。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/version-release/SKILL.md')
    assert "git tag --list | grep -v -E '(experimental|alpha|resource)' | sort -V | tail -20" in text, "expected to find: " + "git tag --list | grep -v -E '(experimental|alpha|resource)' | sort -V | tail -20"[:80]


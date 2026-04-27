"""Behavioral checks for agentsmesh-docsskills-improve-ghmerge-skill-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agentsmesh")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gh-merge/SKILL.md')
    assert '- **识别 GitHub remote 名称**：检查 `git remote -v` 输出，找到指向 `github.com` 的 remote（可能是 `origin`、`github` 或其他名称），后续所有 git push/fetch 命令都使用该 remote 名称' in text, "expected to find: " + '- **识别 GitHub remote 名称**：检查 `git remote -v` 输出，找到指向 `github.com` 的 remote（可能是 `origin`、`github` 或其他名称），后续所有 git push/fetch 命令都使用该 remote 名称'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gh-merge/SKILL.md')
    assert '如果重试 3 次（共等待约 2 分钟）后仍然 `no checks reported`，则明确告知用户"CI 未触发"，**询问用户是否确认合并**，不得自行决定。' in text, "expected to find: " + '如果重试 3 次（共等待约 2 分钟）后仍然 `no checks reported`，则明确告知用户"CI 未触发"，**询问用户是否确认合并**，不得自行决定。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gh-merge/SKILL.md')
    assert '如果 `gh pr checks` 返回 `no checks reported`，这表示 CI 尚未触发，**绝不能**认为"没有 CI"而直接合并。必须重试：' in text, "expected to find: " + '如果 `gh pr checks` 返回 `no checks reported`，这表示 CI 尚未触发，**绝不能**认为"没有 CI"而直接合并。必须重试：'[:80]


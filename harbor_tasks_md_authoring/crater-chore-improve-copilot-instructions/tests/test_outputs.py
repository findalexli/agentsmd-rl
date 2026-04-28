"""Behavioral checks for crater-chore-improve-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/crater")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **改进建议代码**: 在给出修改建议代码时，请注意参考项目其它代码、Workflow 和 lint 配置，并告知用户：**直接应用来自 Copilot 的修改可能导致 Workflow 失败，推荐参考评论本地修改并测试**。' in text, "expected to find: " + '- **改进建议代码**: 在给出修改建议代码时，请注意参考项目其它代码、Workflow 和 lint 配置，并告知用户：**直接应用来自 Copilot 的修改可能导致 Workflow 失败，推荐参考评论本地修改并测试**。'[:80]


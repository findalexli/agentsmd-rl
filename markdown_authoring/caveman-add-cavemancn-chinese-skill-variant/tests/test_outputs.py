"""Behavioral checks for caveman-add-cavemancn-chinese-skill-variant (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/caveman")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('caveman-cn/SKILL.md')
    assert '**普通：** "组件之所以会重复渲染，很可能是因为你在每次渲染时都创建了一个新的对象引用。当这个内联对象作为 prop 传入时，React 的浅比较会把它视为新值，于是触发重渲染。建议用 `useMemo` 缓存这个对象。"' in text, "expected to find: " + '**普通：** "组件之所以会重复渲染，很可能是因为你在每次渲染时都创建了一个新的对象引用。当这个内联对象作为 prop 传入时，React 的浅比较会把它视为新值，于是触发重渲染。建议用 `useMemo` 缓存这个对象。"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('caveman-cn/SKILL.md')
    assert '“更简短”、“少点字”、“用中文 caveman”，或调用 /caveman-cn 时。也适用于明确要求节省 token 的中文对话。' in text, "expected to find: " + '“更简短”、“少点字”、“用中文 caveman”，或调用 /caveman-cn 时。也适用于明确要求节省 token 的中文对话。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('caveman-cn/SKILL.md')
    assert '**Caveman CN：** "每次 render 都新对象引用。prop 浅比较次次变。于是重渲染。包进 `useMemo`。"' in text, "expected to find: " + '**Caveman CN：** "每次 render 都新对象引用。prop 浅比较次次变。于是重渲染。包进 `useMemo`。"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/caveman/skills/caveman-cn/SKILL.md')
    assert '默认强度：**full**。切换：`/caveman-cn lite`、`/caveman-cn full`、`/caveman-cn ultra`。' in text, "expected to find: " + '默认强度：**full**。切换：`/caveman-cn lite`、`/caveman-cn full`、`/caveman-cn ultra`。'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/caveman/skills/caveman-cn/SKILL.md')
    assert '“更简短”、“少点字”、“用中文 caveman”，或调用 /caveman-cn 时。也适用于明确要求节省 token 的中文对话。' in text, "expected to find: " + '“更简短”、“少点字”、“用中文 caveman”，或调用 /caveman-cn 时。也适用于明确要求节省 token 的中文对话。'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/caveman/skills/caveman-cn/SKILL.md')
    assert '**Full：** 每次 render 都新对象引用。prop 浅比较次次变。于是重渲染。包进 `useMemo`。' in text, "expected to find: " + '**Full：** 每次 render 都新对象引用。prop 浅比较次次变。于是重渲染。包进 `useMemo`。'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/caveman-cn/SKILL.md')
    assert '去掉：客套、铺垫、重复解释、空泛总结、无信息量过渡词。优先短句、短分句、短词组。允许残句。技术术语、API 名、变量名、命令、路径、错误消息保持精确。代码块不改。必要风险提示、破坏性操作确认、合规/安全说明恢复正常清晰中文。' in text, "expected to find: " + '去掉：客套、铺垫、重复解释、空泛总结、无信息量过渡词。优先短句、短分句、短词组。允许残句。技术术语、API 名、变量名、命令、路径、错误消息保持精确。代码块不改。必要风险提示、破坏性操作确认、合规/安全说明恢复正常清晰中文。'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/caveman-cn/SKILL.md')
    assert '代码、commit、PR 正常写。用户说“停止 caveman”“normal mode”“恢复正常”就立即退出。级别持续到用户切换或会话结束。' in text, "expected to find: " + '代码、commit、PR 正常写。用户说“停止 caveman”“normal mode”“恢复正常”就立即退出。级别持续到用户切换或会话结束。'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/caveman-cn/SKILL.md')
    assert '“更简短”、“少点字”、“用中文 caveman”，或调用 /caveman-cn 时。也适用于明确要求节省 token 的中文对话。' in text, "expected to find: " + '“更简短”、“少点字”、“用中文 caveman”，或调用 /caveman-cn 时。也适用于明确要求节省 token 的中文对话。'[:80]


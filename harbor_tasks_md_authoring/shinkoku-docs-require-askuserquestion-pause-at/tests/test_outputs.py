"""Behavioral checks for shinkoku-docs-require-askuserquestion-pause-at (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shinkoku")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/e-tax/SKILL.md')
    assert '**AskUserQuestion ツールで一時停止**し、ユーザーが認証完了を報告するまで**絶対に次のステップに進まない**こと。' in text, "expected to find: " + '**AskUserQuestion ツールで一時停止**し、ユーザーが認証完了を報告するまで**絶対に次のステップに進まない**こと。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/e-tax/SKILL.md')
    assert '- 「QRコードが表示されない」が選ばれた場合は下記の ⚠️ Playwright CLI 使用時の注意 を参照して対処する' in text, "expected to find: " + '- 「QRコードが表示されない」が選ばれた場合は下記の ⚠️ Playwright CLI 使用時の注意 を参照して対処する'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/e-tax/SKILL.md')
    assert '- **ユーザーが「認証完了」を選択するまで、一切のブラウザ操作・画面遷移を行わない**' in text, "expected to find: " + '- **ユーザーが「認証完了」を選択するまで、一切のブラウザ操作・画面遷移を行わない**'[:80]


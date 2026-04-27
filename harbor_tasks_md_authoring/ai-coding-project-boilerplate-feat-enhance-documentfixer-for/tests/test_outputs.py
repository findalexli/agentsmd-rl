"""Behavioral checks for ai-coding-project-boilerplate-feat-enhance-documentfixer-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-coding-project-boilerplate")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/document-fixer.md')
    assert 'これらは並列実行され、各レビューは独立したコンテキストで実行されます。上記は各パラメータの使い方を示したもので、実際は「2. レビュー戦略の決定」に記載された観点（整合性検証を除く）を実行します。整合性検証は「6. 整合性検証と微調整」フェーズで単独実行されます。' in text, "expected to find: " + 'これらは並列実行され、各レビューは独立したコンテキストで実行されます。上記は各パラメータの使い方を示したもので、実際は「2. レビュー戦略の決定」に記載された観点（整合性検証を除く）を実行します。整合性検証は「6. 整合性検証と微調整」フェーズで単独実行されます。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/document-fixer.md')
    assert 'prompt="@document-reviewer mode=critical focus=business_perspective doc_type=PRD target=[ドキュメントパス]"' in text, "expected to find: " + 'prompt="@document-reviewer mode=critical focus=business_perspective doc_type=PRD target=[ドキュメントパス]"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/document-fixer.md')
    assert 'この修正により、AIがドキュメントを解釈する際の精度が最大化され、実行時のエラーや誤解釈を防ぎます。内容の正確性は第1次修正で担保済みのため、第2次修正では解釈精度の向上に特化します。' in text, "expected to find: " + 'この修正により、AIがドキュメントを解釈する際の精度が最大化され、実行時のエラーや誤解釈を防ぎます。内容の正確性は第1次修正で担保済みのため、第2次修正では解釈精度の向上に特化します。'[:80]


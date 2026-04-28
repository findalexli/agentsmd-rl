"""Behavioral checks for cursorrules-refactor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cursorrules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-strategy.en.mdc')
    assert '5. In principle, any PR that includes a meaningful change to production code (such as new features, bug fixes, or refactors that may affect behavior) must also include corresponding additions or updat' in text, "expected to find: " + '5. In principle, any PR that includes a meaningful change to production code (such as new features, bug fixes, or refactors that may affect behavior) must also include corresponding additions or updat'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-strategy.en.mdc')
    assert '5. Note: For minor adjustments to existing tests (such as tweaking messages or slightly updating expectations) that do not introduce new branches or constraints, creating or updating a test perspectiv' in text, "expected to find: " + '5. Note: For minor adjustments to existing tests (such as tweaking messages or slightly updating expectations) that do not introduce new branches or constraints, creating or updating a test perspectiv'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-strategy.en.mdc')
    assert '6. If adding or updating tests is reasonably difficult, clearly document the reasons and the alternative verification steps (such as manual test procedures) in the PR description and obtain agreement ' in text, "expected to find: " + '6. If adding or updating tests is reasonably difficult, clearly document the reasons and the alternative verification steps (such as manual test procedures) in the PR description and obtain agreement '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-strategy.mdc')
    assert '2. ブランチカバレッジ・ステートメントカバレッジを確認し、分岐網羅 100% を目標とする（達成が合理的でない場合は、ビジネスインパクトの高い分岐および主要なエラー経路を優先的に網羅すること）。' in text, "expected to find: " + '2. ブランチカバレッジ・ステートメントカバレッジを確認し、分岐網羅 100% を目標とする（達成が合理的でない場合は、ビジネスインパクトの高い分岐および主要なエラー経路を優先的に網羅すること）。'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-strategy.mdc')
    assert '境界値候補（0 / 最小値 / 最大値 / ±1 / 空 / NULL）のうち仕様上意味を持たないものは、`Notes` に対象外とする理由を記載したうえで省略してよい。' in text, "expected to find: " + '境界値候補（0 / 最小値 / 最大値 / ±1 / 空 / NULL）のうち仕様上意味を持たないものは、`Notes` に対象外とする理由を記載したうえで省略してよい。'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-strategy.mdc')
    assert '5. 原則として、本番コードに意味のある変更（仕様追加・バグ修正・挙動に影響し得るリファクタ）を含むPRには、対応する自動テストの追加または更新を必ず含めること。' in text, "expected to find: " + '5. 原則として、本番コードに意味のある変更（仕様追加・バグ修正・挙動に影響し得るリファクタ）を含むPRには、対応する自動テストの追加または更新を必ず含めること。'[:80]


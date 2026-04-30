"""Behavioral checks for ai-agents-for-beginners-translate-skillmd-content-to-japanes (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-agents-for-beginners")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('translations/ja/.agents/skills/jupyter-notebook/SKILL.md')
    assert '本書はAI翻訳サービス「[Co-op Translator](https://github.com/Azure/co-op-translator)」を使用して翻訳されました。正確さには努めていますが、自動翻訳には誤りや不正確な箇所が含まれる可能性があります。原文（原言語の文書）を正本としてご参照ください。重要な情報については、専門の人間による翻訳を推奨します。本翻訳の利用により生じたいかなる誤解や' in text, "expected to find: " + '本書はAI翻訳サービス「[Co-op Translator](https://github.com/Azure/co-op-translator)」を使用して翻訳されました。正確さには努めていますが、自動翻訳には誤りや不正確な箇所が含まれる可能性があります。原文（原言語の文書）を正本としてご参照ください。重要な情報については、専門の人間による翻訳を推奨します。本翻訳の利用により生じたいかなる誤解や'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('translations/ja/.agents/skills/jupyter-notebook/SKILL.md')
    assert '- テンプレートは `assets/experiment-template.ipynb` と `assets/tutorial-template.ipynb` にあります。' in text, "expected to find: " + '- テンプレートは `assets/experiment-template.ipynb` と `assets/tutorial-template.ipynb` にあります。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('translations/ja/.agents/skills/jupyter-notebook/SKILL.md')
    assert 'ユーザー限定スキルは `$CODEX_HOME/skills` ディレクトリにインストールされます（デフォルト：`~/.codex/skills`）。' in text, "expected to find: " + 'ユーザー限定スキルは `$CODEX_HOME/skills` ディレクトリにインストールされます（デフォルト：`~/.codex/skills`）。'[:80]


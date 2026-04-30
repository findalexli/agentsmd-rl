"""Behavioral checks for cli-docslarkdoc-replace-literal-n-examples (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-doc/references/lark-doc-create.md')
    assert '> **⚠️ `\\n` 不是换行：** `--markdown "...\\n..."` 里的 `\\n` 在 shell 里是字面反斜杠 + n，会作为文字写入文档。请用真实换行：多行字符串、heredoc (`--markdown -`)、或 `$\'...\\n...\'`（bash/zsh）。示例见下方。' in text, "expected to find: " + '> **⚠️ `\\n` 不是换行：** `--markdown "...\\n..."` 里的 `\\n` 在 shell 里是字面反斜杠 + n，会作为文字写入文档。请用真实换行：多行字符串、heredoc (`--markdown -`)、或 `$\'...\\n...\'`（bash/zsh）。示例见下方。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-doc/references/lark-doc-create.md')
    assert 'lark-cli docs +create --title "产品需求" --markdown \'<callout emoji="💡" background-color="light-blue">' in text, "expected to find: " + 'lark-cli docs +create --title "产品需求" --markdown \'<callout emoji="💡" background-color="light-blue">'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-doc/references/lark-doc-create.md')
    assert 'lark-cli docs +create --title "会议纪要" --folder-token fldcnXXXX --markdown "## 讨论议题' in text, "expected to find: " + 'lark-cli docs +create --title "会议纪要" --folder-token fldcnXXXX --markdown "## 讨论议题'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-doc/references/lark-doc-update.md')
    assert '> **⚠️ `\\n` 不是换行：** `--markdown "...\\n..."` 里的 `\\n` 在 shell 里是字面反斜杠 + n，会作为文字写入文档。请用真实换行：多行字符串、heredoc (`--markdown -`)、或 `$\'...\\n...\'`（bash/zsh）。示例见下方。' in text, "expected to find: " + '> **⚠️ `\\n` 不是换行：** `--markdown "...\\n..."` 里的 `\\n` 在 shell 里是字面反斜杠 + n，会作为文字写入文档。请用真实换行：多行字符串、heredoc (`--markdown -`)、或 `$\'...\\n...\'`（bash/zsh）。示例见下方。'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-doc/references/lark-doc-update.md')
    assert 'lark-cli docs +update --doc "文档ID" --mode replace_range --selection-with-ellipsis "## 旧标题...旧结尾。" --markdown "## 新标题' in text, "expected to find: " + 'lark-cli docs +update --doc "文档ID" --mode replace_range --selection-with-ellipsis "## 旧标题...旧结尾。" --markdown "## 新标题'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-doc/references/lark-doc-update.md')
    assert 'lark-cli docs +update --doc "<doc_id>" --mode replace_range --selection-by-title "## 功能说明" --markdown "## 功能说明' in text, "expected to find: " + 'lark-cli docs +update --doc "<doc_id>" --mode replace_range --selection-by-title "## 功能说明" --markdown "## 功能说明'[:80]


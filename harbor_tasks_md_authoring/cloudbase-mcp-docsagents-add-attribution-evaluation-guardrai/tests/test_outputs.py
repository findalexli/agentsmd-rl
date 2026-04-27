"""Behavioral checks for cloudbase-mcp-docsagents-add-attribution-evaluation-guardrai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cloudbase-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '4. 不要在代码、注释、文档、提交说明或 PR 描述中泄漏内部评测文件名或上下文路径（例如 `run-result.json`、`run-trace.json`、`evaluation-trace.json`、`.codebuddy/attribution-context`）；如必须提及，统一改写为“internal evaluation evidence”。' in text, "expected to find: " + '4. 不要在代码、注释、文档、提交说明或 PR 描述中泄漏内部评测文件名或上下文路径（例如 `run-result.json`、`run-trace.json`、`evaluation-trace.json`、`.codebuddy/attribution-context`）；如必须提及，统一改写为“internal evaluation evidence”。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '当任务来源于 failing eval、attribution issue、grader、benchmark、trace、result artifact 或其他评测证据时，必须额外遵守以下规则：' in text, "expected to find: " + '当任务来源于 failing eval、attribution issue、grader、benchmark、trace、result artifact 或其他评测证据时，必须额外遵守以下规则：'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '5. 如果证据更像 grader / task contract 问题、仓库路由错误、或外部系统限制，而不是当前仓库里的真实产品缺陷，应停止产品表面改动，并在总结里明确说明原因与后续建议。' in text, "expected to find: " + '5. 如果证据更像 grader / task contract 问题、仓库路由错误、或外部系统限制，而不是当前仓库里的真实产品缺陷，应停止产品表面改动，并在总结里明确说明原因与后续建议。'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('mcp/AGENTS.md')
    assert '- Do not leak internal evaluation filenames or context paths in code, comments, docs, commit messages, or PR bodies, including `run-result.json`, `run-trace.json`, `evaluation-trace.json`, and `.codeb' in text, "expected to find: " + '- Do not leak internal evaluation filenames or context paths in code, comments, docs, commit messages, or PR bodies, including `run-result.json`, `run-trace.json`, `evaluation-trace.json`, and `.codeb'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('mcp/AGENTS.md')
    assert '- If the evidence points to a grader mismatch, task-contract mismatch, wrong-repo routing, or external limitation rather than a real product defect here, stop product-surface edits and explain that in' in text, "expected to find: " + '- If the evidence points to a grader mismatch, task-contract mismatch, wrong-repo routing, or external limitation rather than a real product defect here, stop product-surface edits and explain that in'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('mcp/AGENTS.md')
    assert 'When a task is triggered by failing evaluations, attribution issues, grader output, benchmark evidence, traces, or result artifacts, treat that evidence as diagnosis input rather than a public product' in text, "expected to find: " + 'When a task is triggered by failing evaluations, attribution issues, grader output, benchmark evidence, traces, or result artifacts, treat that evidence as diagnosis input rather than a public product'[:80]


"""Behavioral checks for anolisa-featskills-add-promptscanner-skill-definition (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/anolisa")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/agent-sec-core/skills/prompt-scanner/SKILL.md')
    assert 'description: 使用 agent-sec-cli 扫描 prompt 文本中的注入攻击和越狱尝试，返回结构化 JSON 扫描结果。当用户提到 prompt 安全、prompt 注入检测、越狱检测、提示词攻击检测，或者需要判断一段文本是否包含恶意 prompt 注入时，都应使用此技能。即使用户没有明确说"扫描"，只要涉及评估 prompt 文本的安全性，也应触发此技能。' in text, "expected to find: " + 'description: 使用 agent-sec-cli 扫描 prompt 文本中的注入攻击和越狱尝试，返回结构化 JSON 扫描结果。当用户提到 prompt 安全、prompt 注入检测、越狱检测、提示词攻击检测，或者需要判断一段文本是否包含恶意 prompt 注入时，都应使用此技能。即使用户没有明确说"扫描"，只要涉及评估 prompt 文本的安全性，也应触发此技能。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/agent-sec-core/skills/prompt-scanner/SKILL.md')
    assert '- 如果 ML 依赖未安装（未执行 `uv sync --extra ml`），scanner 会自动降级为仅 L1 模式并输出 WARNING 日志，不会报错。此时 `--mode standard` 实际只执行 L1。' in text, "expected to find: " + '- 如果 ML 依赖未安装（未执行 `uv sync --extra ml`），scanner 会自动降级为仅 L1 模式并输出 WARNING 日志，不会报错。此时 `--mode standard` 实际只执行 L1。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/agent-sec-core/skills/prompt-scanner/SKILL.md')
    assert '- **`threat_type`**：威胁类型——`direct_injection`（直接注入）、`indirect_injection`（间接注入）、`jailbreak`（越狱）、`benign`（良性）' in text, "expected to find: " + '- **`threat_type`**：威胁类型——`direct_injection`（直接注入）、`indirect_injection`（间接注入）、`jailbreak`（越狱）、`benign`（良性）'[:80]


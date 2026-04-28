"""Behavioral checks for finlab-ai-skillmd-make-quota-error-handling (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/finlab-ai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('finlab-plugin/skills/finlab/SKILL.md')
    assert '當出現 `Usage exceed 500 MB/day` 或類似用量超限錯誤時，**主動**告知用戶：' in text, "expected to find: " + '當出現 `Usage exceed 500 MB/day` 或類似用量超限錯誤時，**主動**告知用戶：'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('finlab-plugin/skills/finlab/SKILL.md')
    assert '4. 升級連結：https://www.finlab.finance/payment' in text, "expected to find: " + '4. 升級連結：https://www.finlab.finance/payment'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('finlab-plugin/skills/finlab/SKILL.md')
    assert '3. 升級 VIP 可享 5000 MB 額度（10 倍）' in text, "expected to find: " + '3. 升級 VIP 可享 5000 MB 額度（10 倍）'[:80]


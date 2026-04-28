"""Behavioral checks for day1global-skills-skillmd-skillssh-clawhubai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/day1global-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'description: 科技股财报深度分析与多视角投资备忘录系统（v3.0）。覆盖A-P共16大分析模块、6大投资哲学视角、机构级证据标准、反偏见框架和可执行决策体系。当用户提到某科技公司财报分析、季报/年报解读、earnings call、收入增长分析、利润率变化、guidance指引、估值模型、DCF、反向DCF、EV/EBITDA、PEG、Rule of 40、管理层分析、竞争格局、持仓判' in text, "expected to find: " + 'description: 科技股财报深度分析与多视角投资备忘录系统（v3.0）。覆盖A-P共16大分析模块、6大投资哲学视角、机构级证据标准、反偏见框架和可执行决策体系。当用户提到某科技公司财报分析、季报/年报解读、earnings call、收入增长分析、利润率变化、guidance指引、估值模型、DCF、反向DCF、EV/EBITDA、PEG、Rule of 40、管理层分析、竞争格局、持仓判'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '| 第一层 | 一手来源（Primary） | CEO原话、员工评价（Glassdoor/Blind）、客户评价（G2/AppStore）、GitHub活跃度、专利申请、招聘动向、内部人交易 | 全报告至少3个 |' in text, "expected to find: " + '| 第一层 | 一手来源（Primary） | CEO原话、员工评价（Glassdoor/Blind）、客户评价（G2/AppStore）、GitHub活跃度、专利申请、招聘动向、内部人交易 | 全报告至少3个 |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**反模式警告**：与Key Forces直接相关的模块应获得2-3倍篇幅。如果分析像一份"什么都涉及但什么都不深入"的清单，就是Key Forces没找准。' in text, "expected to find: " + '**反模式警告**：与Key Forces直接相关的模块应获得2-3倍篇幅。如果分析像一份"什么都涉及但什么都不深入"的清单，就是Key Forces没找准。'[:80]


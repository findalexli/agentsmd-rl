"""Behavioral checks for cli-fix-add-recordsharelinkcreate-in-skillmd (markdown_authoring task).

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
    text = _read('skills/lark-base/SKILL.md')
    assert 'description: "当需要用 lark-cli 操作飞书多维表格（Base）时调用：适用于建表、字段管理、记录读写、记录分享链接、视图配置、历史查询，以及角色/表单/仪表盘管理/工作流；也适用于把旧的 +table / +field / +record 写法改成当前命令写法。涉及字段设计、公式字段、查找引用、跨表计算、行级派生指标、数据分析需求时也必须使用本 skill。"' in text, "expected to find: " + 'description: "当需要用 lark-cli 操作飞书多维表格（Base）时调用：适用于建表、字段管理、记录读写、记录分享链接、视图配置、历史查询，以及角色/表单/仪表盘管理/工作流；也适用于把旧的 +table / +field / +record 写法改成当前命令写法。涉及字段设计、公式字段、查找引用、跨表计算、行级派生指标、数据分析需求时也必须使用本 skill。"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-base/SKILL.md')
    assert '| `+record-share-link-create` | 为一条或多条记录生成分享链接 | [`lark-base-record-share-link-create.md`](references/lark-base-record-share-link-create.md) | 单次最多 100 条；重复 record_id 会自动去重；适合分享单条记录或批量分享场景 |' in text, "expected to find: " + '| `+record-share-link-create` | 为一条或多条记录生成分享链接 | [`lark-base-record-share-link-create.md`](references/lark-base-record-share-link-create.md) | 单次最多 100 条；重复 record_id 会自动去重；适合分享单条记录或批量分享场景 |'[:80]


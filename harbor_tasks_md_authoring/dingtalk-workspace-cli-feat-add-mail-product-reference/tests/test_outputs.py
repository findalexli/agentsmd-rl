"""Behavioral checks for dingtalk-workspace-cli-feat-add-mail-product-reference (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dingtalk-workspace-cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/SKILL.md')
    assert 'description: 管理钉钉产品能力(AI表格/日历/通讯录/群聊与机器人/待办/审批/考勤/日志/DING消息/开放平台文档/钉钉文档/钉钉云盘/AI听记/邮箱等)。当用户需要操作表格数据、管理日程会议、查询通讯录、管理群聊、机器人发消息、创建待办、提交审批、查看考勤、提交日报周报（钉钉日志模版）、读写钉钉文档、上传下载云盘文件、查询听记纪要、收发邮件时使用。' in text, "expected to find: " + 'description: 管理钉钉产品能力(AI表格/日历/通讯录/群聊与机器人/待办/审批/考勤/日志/DING消息/开放平台文档/钉钉文档/钉钉云盘/AI听记/邮箱等)。当用户需要操作表格数据、管理日程会议、查询通讯录、管理群聊、机器人发消息、创建待办、提交审批、查看考勤、提交日报周报（钉钉日志模版）、读写钉钉文档、上传下载云盘文件、查询听记纪要、收发邮件时使用。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/SKILL.md')
    assert '| `mail`            | 邮箱：邮箱地址查询/邮件搜索(KQL)/邮件详情/发送邮件                        | [mail.md](./references/products/mail.md)                       |' in text, "expected to find: " + '| `mail`            | 邮箱：邮箱地址查询/邮件搜索(KQL)/邮件详情/发送邮件                        | [mail.md](./references/products/mail.md)                       |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/SKILL.md')
    assert '用户提到"邮箱/邮件/发邮件/收邮件/搜邮件/查邮件" → `mail`' in text, "expected to find: " + '用户提到"邮箱/邮件/发邮件/收邮件/搜邮件/查邮件" → `mail`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/references/products/mail.md')
    assert '| `from` | 字符串（邮件地址或名称） | 发件人，支持：纯邮件地址、纯名称（含空格须加双引号）、`"名称<邮件地址>"` 格式 | `from:alice@company.com`、`from:"张 三"`、`from:"alice<a@b.com>"` | `from:张 三`（含空格未加引号） |' in text, "expected to find: " + '| `from` | 字符串（邮件地址或名称） | 发件人，支持：纯邮件地址、纯名称（含空格须加双引号）、`"名称<邮件地址>"` 格式 | `from:alice@company.com`、`from:"张 三"`、`from:"alice<a@b.com>"` | `from:张 三`（含空格未加引号） |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/references/products/mail.md')
    assert '- 收件人邮箱获取：用户只知道同事名字时，先通过 `dws aisearch person --keyword "名字" --dimension name` 获取 userId，再 `dws contact user get --ids <userId>` 从返回中提取 orgAuthEmail 字段' in text, "expected to find: " + '- 收件人邮箱获取：用户只知道同事名字时，先通过 `dws aisearch person --keyword "名字" --dimension name` 获取 userId，再 `dws contact user get --ids <userId>` 从返回中提取 orgAuthEmail 字段'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/references/products/mail.md')
    assert '| `to` | 字符串（邮件地址或名称） | 收件人，支持：纯邮件地址、纯名称（含空格须加双引号）、`"名称<邮件地址>"` 格式 | `to:bob@company.com`、`to:"李 四"`、`to:"alice<a@b.com>"` | `to:李 四`（含空格未加引号） |' in text, "expected to find: " + '| `to` | 字符串（邮件地址或名称） | 收件人，支持：纯邮件地址、纯名称（含空格须加双引号）、`"名称<邮件地址>"` 格式 | `to:bob@company.com`、`to:"李 四"`、`to:"alice<a@b.com>"` | `to:李 四`（含空格未加引号） |'[:80]


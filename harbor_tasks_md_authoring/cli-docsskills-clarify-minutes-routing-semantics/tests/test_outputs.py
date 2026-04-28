"""Behavioral checks for cli-docsskills-clarify-minutes-routing-semantics (markdown_authoring task).

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
    text = _read('skills/lark-minutes/SKILL.md')
    assert '> - 用户如果要的是妙记基础信息，拿到 `minute_token` 后用 `minutes minutes get`；用户如果要的是逐字稿、总结、待办、章节，再走 `vc +notes --minute-tokens`' in text, "expected to find: " + '> - 用户如果要的是妙记基础信息，拿到 `minute_token` 后用 `minutes minutes get`；用户如果要的是逐字稿、总结、待办、章节，再走 `vc +notes --minute-tokens`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-minutes/SKILL.md')
    assert '5. 会议场景的妙记路由，以及"参与的妙记"如何解释，统一以 [minutes +search](references/lark-minutes-search.md) 为准。' in text, "expected to find: " + '5. 会议场景的妙记路由，以及"参与的妙记"如何解释，统一以 [minutes +search](references/lark-minutes-search.md) 为准。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-minutes/SKILL.md')
    assert '> - “我的妙记”“参与的妙记”等自然语言映射细则，以 [minutes +search](references/lark-minutes-search.md) 为准' in text, "expected to find: " + '> - “我的妙记”“参与的妙记”等自然语言映射细则，以 [minutes +search](references/lark-minutes-search.md) 为准'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-minutes/references/lark-minutes-download.md')
    assert '| 会议录制查询 | `lark-cli vc +recording --meeting-ids <id>` 或 `lark-cli vc +recording --calendar-event-ids <event_id>` |' in text, "expected to find: " + '| 会议录制查询 | `lark-cli vc +recording --meeting-ids <id>` 或 `lark-cli vc +recording --calendar-event-ids <event_id>` |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-minutes/references/lark-minutes-search.md')
    assert '- 当用户同时提到“会议 / 会 / 开会 / 某场会”和“妙记”时，优先先定位会议；如果要的是妙记信息，走 `vc +recording` → `minutes minutes get`，只有要纪要内容时才走 `vc +notes --minute-tokens`。' in text, "expected to find: " + '- 当用户同时提到“会议 / 会 / 开会 / 某场会”和“妙记”时，优先先定位会议；如果要的是妙记信息，走 `vc +recording` → `minutes minutes get`，只有要纪要内容时才走 `vc +notes --minute-tokens`。'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-minutes/references/lark-minutes-search.md')
    assert '不要只跑一次 `--participant-ids me` 就直接下结论，也不要把 `--owner-ids me` 和 `--participant-ids me` 同时塞进一次查询里赌接口语义。应分别查询后，按 `token` 做并集去重。' in text, "expected to find: " + '不要只跑一次 `--participant-ids me` 就直接下结论，也不要把 `--owner-ids me` 和 `--participant-ids me` 同时塞进一次查询里赌接口语义。应分别查询后，按 `token` 做并集去重。'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-minutes/references/lark-minutes-search.md')
    assert 'lark-cli minutes +search --participant-ids "me" --start 2026-03-10 --end 2026-03-10' in text, "expected to find: " + 'lark-cli minutes +search --participant-ids "me" --start 2026-03-10 --end 2026-03-10'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-vc/SKILL.md')
    assert '> **妙记边界**：`+notes` 负责纪要内容、逐字稿和 AI 产物；妙记基础信息请优先看 [`+recording`](references/lark-vc-recording.md) 与 [lark-minutes](../lark-minutes/SKILL.md)。' in text, "expected to find: " + '> **妙记边界**：`+notes` 负责纪要内容、逐字稿和 AI 产物；妙记基础信息请优先看 [`+recording`](references/lark-vc-recording.md) 与 [lark-minutes](../lark-minutes/SKILL.md)。'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-vc/references/lark-vc-recording.md')
    assert '> **边界提醒：** 如果用户明确要的是"妙记信息""妙记详情""妙记链接""minute_token""标题""时长""owner"这类妙记元信息，先用本命令拿到 `minute_token`，再调用 `minutes minutes get`。不要直接切到 `vc +notes`；`vc +notes` 只用于纪要内容和逐字稿。' in text, "expected to find: " + '> **边界提醒：** 如果用户明确要的是"妙记信息""妙记详情""妙记链接""minute_token""标题""时长""owner"这类妙记元信息，先用本命令拿到 `minute_token`，再调用 `minutes minutes get`。不要直接切到 `vc +notes`；`vc +notes` 只用于纪要内容和逐字稿。'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-vc/references/lark-vc-recording.md')
    assert '- 拿到 `minute_token` 后，如果要妙记基础信息，优先传给 `minutes minutes get`；如果要下载媒体文件，传给 `minutes +download`；如果要逐字稿、总结、待办、章节，再传给 `vc +notes --minute-tokens`。' in text, "expected to find: " + '- 拿到 `minute_token` 后，如果要妙记基础信息，优先传给 `minutes minutes get`；如果要下载媒体文件，传给 `minutes +download`；如果要逐字稿、总结、待办、章节，再传给 `vc +notes --minute-tokens`。'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-vc/references/lark-vc-recording.md')
    assert 'lark-cli minutes minutes get --params \'{"minute_token":"<minute_token>"}\'' in text, "expected to find: " + 'lark-cli minutes minutes get --params \'{"minute_token":"<minute_token>"}\''[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-vc/references/lark-vc-search.md')
    assert 'lark-cli minutes minutes get --params \'{"minute_token":"<MINUTE_TOKEN>"}\'' in text, "expected to find: " + 'lark-cli minutes minutes get --params \'{"minute_token":"<MINUTE_TOKEN>"}\''[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-vc/references/lark-vc-search.md')
    assert '- [lark-vc-recording](lark-vc-recording.md) -- 查询会议对应的 minute_token' in text, "expected to find: " + '- [lark-vc-recording](lark-vc-recording.md) -- 查询会议对应的 minute_token'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-vc/references/lark-vc-search.md')
    assert '- 用户如果明确问的是“妙记信息”而不是“纪要内容”，不要默认走 `vc +notes`；应先用 `vc +recording`。' in text, "expected to find: " + '- 用户如果明确问的是“妙记信息”而不是“纪要内容”，不要默认走 `vc +notes`；应先用 `vc +recording`。'[:80]


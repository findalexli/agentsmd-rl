"""Behavioral checks for prism-insight-docs-update-claudemd-v250 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prism-insight")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| 2.5.0 | 2026-02-22 | **Telegram /report 일일 횟수 환급 + 한국어 메시지 복원** - 서버 오류(서브프로세스 타임아웃, 내부 AI 에이전트 오류) 시 `/report`·`/us_report` 일일 사용 횟수 자동 환급 (`refund_daily_limit`, `_is_server_error` 추가, `send_report' in text, "expected to find: " + '| 2.5.0 | 2026-02-22 | **Telegram /report 일일 횟수 환급 + 한국어 메시지 복원** - 서버 오류(서브프로세스 타임아웃, 내부 AI 에이전트 오류) 시 `/report`·`/us_report` 일일 사용 횟수 자동 환급 (`refund_daily_limit`, `_is_server_error` 추가, `send_report'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `/report` 오류 후 재사용 불가 | v2.5.0 수정 - 서버 오류 시 자동 환급됨, 재시도 가능 |' in text, "expected to find: " + '| `/report` 오류 후 재사용 불가 | v2.5.0 수정 - 서버 오류 시 자동 환급됨, 재시도 가능 |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '> **Version**: 2.5.0 | **Updated**: 2026-02-22' in text, "expected to find: " + '> **Version**: 2.5.0 | **Updated**: 2026-02-22'[:80]


"""Behavioral checks for moai-adk-fixworkflow-askuserquestion-enforcement-protocol-19 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/moai-adk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/moai/SKILL.md')
    assert '| "Schema 로드가 귀찮으니 이번엔 산문으로 질문하자" | AskUserQuestion/Task* 는 deferred tool. ToolSearch 한 번으로 session 전체 사용 가능. 산문 질문은 HARD 위반 (CLAUDE.md §1, §8 Deferred Tool Preload Protocol). |' in text, "expected to find: " + '| "Schema 로드가 귀찮으니 이번엔 산문으로 질문하자" | AskUserQuestion/Task* 는 deferred tool. ToolSearch 한 번으로 session 전체 사용 가능. 산문 질문은 HARD 위반 (CLAUDE.md §1, §8 Deferred Tool Preload Protocol). |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/moai/SKILL.md')
    assert '| "짧은 확인 질문은 산문으로 처리해도 된다" | 모든 user-facing 질문은 AskUserQuestion 경유 강제. "짧은 질문"은 예외 아님. Self-check: 응답에 "?" 있으면 AskUserQuestion 호출 동반 필수. |' in text, "expected to find: " + '| "짧은 확인 질문은 산문으로 처리해도 된다" | 모든 user-facing 질문은 AskUserQuestion 경유 강제. "짧은 질문"은 예외 아님. Self-check: 응답에 "?" 있으면 AskUserQuestion 호출 동반 필수. |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/moai/SKILL.md')
    assert '- [ ] Session opened with ToolSearch preload of deferred tools (AskUserQuestion, TaskCreate/Update/List/Get)' in text, "expected to find: " + '- [ ] Session opened with ToolSearch preload of deferred tools (AskUserQuestion, TaskCreate/Update/List/Get)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.local.md')
    assert '2026-04-24 세션에서 `AskUserQuestion` 미사용으로 [HARD] 규칙(§1, §8) 위반 반복 발생. 근본 원인은 **deferred tool 사전 로드 부재** + **산문 질문 편의주의**. v3.4.0부터 본 Enforcement Protocol을 [HARD] 운영 방침으로 고정.' in text, "expected to find: " + '2026-04-24 세션에서 `AskUserQuestion` 미사용으로 [HARD] 규칙(§1, §8) 위반 반복 발생. 근본 원인은 **deferred tool 사전 로드 부재** + **산문 질문 편의주의**. v3.4.0부터 본 Enforcement Protocol을 [HARD] 운영 방침으로 고정.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.local.md')
    assert '1. **1차 원인**: `AskUserQuestion`은 deferred tool. 세션 시작 시 schema 미로드 → 직접 호출 시 `InputValidationError` → agent가 회피 → 산문 질문으로 우회.' in text, "expected to find: " + '1. **1차 원인**: `AskUserQuestion`은 deferred tool. 세션 시작 시 schema 미로드 → 직접 호출 시 `InputValidationError` → agent가 회피 → 산문 질문으로 우회.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.local.md')
    assert '2. **Option list detection**: 응답에 선택지 구조(`- A:`, `- B:`, `Option X:`, `1.`)가 있는가? → structured `AskUserQuestion` 경유 필수' in text, "expected to find: " + '2. **Option list detection**: 응답에 선택지 구조(`- A:`, `- B:`, `Option X:`, `1.`)가 있는가? → structured `AskUserQuestion` 경유 필수'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- [HARD] Deferred Tool Preload: AskUserQuestion, TaskCreate/Update/List/Get are deferred tools — schema is NOT loaded at session start. Call ToolSearch BEFORE first use to load schemas. Calling withou' in text, "expected to find: " + '- [HARD] Deferred Tool Preload: AskUserQuestion, TaskCreate/Update/List/Get are deferred tools — schema is NOT loaded at session start. Call ToolSearch BEFORE first use to load schemas. Calling withou'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '[HARD] `AskUserQuestion`, `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet` are **deferred tools** — their schemas are NOT loaded at session start. Calling them directly produces `InputValidationError' in text, "expected to find: " + '[HARD] `AskUserQuestion`, `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet` are **deferred tools** — their schemas are NOT loaded at session start. Calling them directly produces `InputValidationError'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. Does the response end with "?" or contain "?" as a decision prompt? → MUST be paired with AskUserQuestion tool call' in text, "expected to find: " + '1. Does the response end with "?" or contain "?" as a decision prompt? → MUST be paired with AskUserQuestion tool call'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/template/templates/.claude/skills/moai/SKILL.md')
    assert '| "Schema 로드가 귀찮으니 이번엔 산문으로 질문하자" | AskUserQuestion/Task* 는 deferred tool. ToolSearch 한 번으로 session 전체 사용 가능. 산문 질문은 HARD 위반 (CLAUDE.md §1, §8 Deferred Tool Preload Protocol). |' in text, "expected to find: " + '| "Schema 로드가 귀찮으니 이번엔 산문으로 질문하자" | AskUserQuestion/Task* 는 deferred tool. ToolSearch 한 번으로 session 전체 사용 가능. 산문 질문은 HARD 위반 (CLAUDE.md §1, §8 Deferred Tool Preload Protocol). |'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/template/templates/.claude/skills/moai/SKILL.md')
    assert '| "짧은 확인 질문은 산문으로 처리해도 된다" | 모든 user-facing 질문은 AskUserQuestion 경유 강제. "짧은 질문"은 예외 아님. Self-check: 응답에 "?" 있으면 AskUserQuestion 호출 동반 필수. |' in text, "expected to find: " + '| "짧은 확인 질문은 산문으로 처리해도 된다" | 모든 user-facing 질문은 AskUserQuestion 경유 강제. "짧은 질문"은 예외 아님. Self-check: 응답에 "?" 있으면 AskUserQuestion 호출 동반 필수. |'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/template/templates/.claude/skills/moai/SKILL.md')
    assert '- [ ] Session opened with ToolSearch preload of deferred tools (AskUserQuestion, TaskCreate/Update/List/Get)' in text, "expected to find: " + '- [ ] Session opened with ToolSearch preload of deferred tools (AskUserQuestion, TaskCreate/Update/List/Get)'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/template/templates/CLAUDE.md')
    assert '- [HARD] Deferred Tool Preload: AskUserQuestion, TaskCreate/Update/List/Get are deferred tools — schema is NOT loaded at session start. Call ToolSearch BEFORE first use to load schemas. Calling withou' in text, "expected to find: " + '- [HARD] Deferred Tool Preload: AskUserQuestion, TaskCreate/Update/List/Get are deferred tools — schema is NOT loaded at session start. Call ToolSearch BEFORE first use to load schemas. Calling withou'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/template/templates/CLAUDE.md')
    assert '[HARD] `AskUserQuestion`, `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet` are **deferred tools** — their schemas are NOT loaded at session start. Calling them directly produces `InputValidationError' in text, "expected to find: " + '[HARD] `AskUserQuestion`, `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet` are **deferred tools** — their schemas are NOT loaded at session start. Calling them directly produces `InputValidationError'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/template/templates/CLAUDE.md')
    assert '1. Does the response end with "?" or contain "?" as a decision prompt? → MUST be paired with AskUserQuestion tool call' in text, "expected to find: " + '1. Does the response end with "?" or contain "?" as a decision prompt? → MUST be paired with AskUserQuestion tool call'[:80]


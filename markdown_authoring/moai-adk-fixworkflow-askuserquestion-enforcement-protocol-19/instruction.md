# fix(workflow): AskUserQuestion Enforcement Protocol (§19 신설 + Red Flags 강화)

Source: [modu-ai/moai-adk#708](https://github.com/modu-ai/moai-adk/pull/708)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/moai/SKILL.md`
- `CLAUDE.local.md`
- `CLAUDE.md`
- `internal/template/templates/.claude/skills/moai/SKILL.md`
- `internal/template/templates/CLAUDE.md`

## What to add / change

## Summary

2026-04-24 세션에서 `AskUserQuestion` 미사용으로 [HARD] §1/§8 규칙이 반복 위반되는 systemic 문제 발견. 근본 원인 3단계 분석 후 **template-first rule 준수**하여 5개 파일 동기화 수정 + memory lesson 기록.

## Root Cause Chain

1. **1차**: `AskUserQuestion`은 deferred tool. 세션 시작 시 schema 미로드 → 호출 시 `InputValidationError` → agent가 회피 → 산문 질문으로 우회.
2. **2차**: Red Flags / Verification 체크리스트에 "응답 말미 `?` + AskUserQuestion 미호출" 탐지 규칙 부재.
3. **3차**: 규칙은 존재하나 enforcement 메커니즘 없이 해석 의존. "짧은 질문은 산문으로" 편의주의 관행.

## Changes

### CLAUDE.md (project + template 동기화)
- **§1 HARD Rules**: "Deferred Tool Preload" 신설 — AskUserQuestion, TaskCreate/Update/List/Get 사전 로드 의무
- **§8 Deferred Tool Preload Protocol [HARD]**: 새 subsection 추가
  - Preload triggers (5개 조건)
  - `ToolSearch` 명령어 예시
  - 5가지 Anti-patterns
  - Pre-response self-check (4 steps)
  - Self-check failure = HARD 위반 선언

### .claude/skills/moai/SKILL.md (project + template 동기화)
- **Common Rationalizations**: 2 rows 추가 (편의주의 거부 근거)
- **Red Flags**: 5 items 추가
  - 응답 ?로 끝나는데 AskUserQuestion 미호출
  - `- A:`, `- B:` 선택지 markdown-only
  - 산문 decision request (`A or B?`)
  - ToolSearch preload 누락
  - Silent wait state
- **Verification**: 4 items 추가 (세션 preload + ? detection + option list routing + silent wait absence)

### CLAUDE.local.md §19 AskUserQuestion Enforcement Protocol (신설, +82 lines)
- §19.1 근본 원인 체인 (3 layers)
- §19.2 [HARD] 세션 시작 Preload 의무
- §19.3 [HARD] Pre-Response Self-Check (4 steps)
- §19.4 [HARD] Anti-Patterns 표
- §19.5 Role별 운영 (orchestrator / subagent / us

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

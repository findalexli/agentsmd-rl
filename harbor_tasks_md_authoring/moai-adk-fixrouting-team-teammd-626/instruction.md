# fix(routing): --team 플래그가 team/*.md 워크플로우를 로드하도록 수정 (#626)

Source: [modu-ai/moai-adk#654](https://github.com/modu-ai/moai-adk/pull/654)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/moai/SKILL.md`
- `internal/template/templates/.claude/skills/moai/SKILL.md`

## What to add / change

## Summary

PR #635에서 분리된 첫 번째 PR. **#626 라우팅 결함 fix만** 포함. astgrep / gopls 구현은 별도 PR로 분리됨.

`.claude/skills/moai/SKILL.md` Step 3에서 `--team` 플래그 파싱 시 `team/<name>.md` 경로를 우선 로드하는 조건 추가. Quick Reference의 plan/run/sync 서브커맨드에 `(team mode: ...)` 경로 명시.

## Changes

- `.claude/skills/moai/SKILL.md` (8 lines)
- `internal/template/templates/.claude/skills/moai/SKILL.md` (47 lines)

총 2 파일, +47/-8.

## Test Plan

- [ ] `/moai run SPEC-XXX --team` 실행 시 `team/run.md` 로드 확인
- [ ] `/moai plan "task" --team` 실행 시 `team/plan.md` 로드 확인
- [ ] `/moai sync --team` 실행 시 `team/sync.md` 로드 확인
- [ ] `--solo` 또는 플래그 없는 경우 기존 `workflows/<name>.md` 로드 확인

## Background — PR #635 Split

원래 PR #635는 #626 fix(routing) + SPEC-ASTG-UPGRADE-001 + SPEC-GOPLS-BRIDGE-001 + 기타가 번들링되어 있어 (107파일 +6028/-911) 3-perspective 리뷰에서 CRITICAL scope creep로 분류됨 (#641 meta 이슈).

본 PR은 그 split의 첫 결과로, **순수 #626 fix만** 포함. 다음 2개 PR이 후속:
- `feat/astgrep-upgrade` (SPEC-ASTG-UPGRADE-001)
- `feat/gopls-bridge` (SPEC-GOPLS-BRIDGE-001)

이로써 #626는 본 PR 머지 시 즉시 종료, #641 meta 이슈는 3개 PR 모두 생성 후 종료.

Fixes #626

🗿 MoAI <email@mo.ai.kr>

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **New Features**
  * Added support for team-mode workflow orchestration selection via `--team` flag

* **Documentation**
  * Enhanced workflow documentation with conditional team-mode file loading
  * Added compliance and verification guidelines to workflow processes

<!-- end of auto-generated comm

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

# docs: add splitVariantProps convention to AGENTS.md and create-component skill

Source: [daangn/seed-design#1363](https://github.com/daangn/seed-design/pull/1363)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/create-component/SKILL.md`
- `.agents/skills/create-component/details/implementation-steps.md`
- `packages/react/AGENTS.md`

## What to add / change

## Summary
- `packages/react/AGENTS.md`에 variant props 처리 패턴 3가지 문서화 (직접 splitVariantProps, createRecipeContext, createSlotRecipeContext)
- `create-component` 스킬에 "AGENTS.md를 먼저 읽고 컨벤션 확인" 단계 추가
- 수동 variant destructuring 안티패턴 경고 추가

## Context
`karby/image-frame-fallback-slot` 리뷰에서 `recipe({ stroke, rounded })` 대신 `recipe.splitVariantProps(props)` 사용이 지적됨. 코드베이스 260+ 파일이 이미 올바른 패턴을 사용하지만, AGENTS.md와 스킬에 이 패턴이 문서화되지 않아 AI가 구식 패턴으로 코드를 생성할 수 있는 문제.

## Test plan
- [x] 변경된 예시가 실제 코드(Badge.tsx, Fab.tsx, Chip.tsx)와 일치 확인
- [x] skill-creator eval로 with/without 비교 완료

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

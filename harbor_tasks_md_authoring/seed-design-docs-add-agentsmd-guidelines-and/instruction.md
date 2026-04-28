# docs: add AGENTS.md guidelines and update create-component skill

Source: [daangn/seed-design#1331](https://github.com/daangn/seed-design/pull/1331)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/create-component/SKILL.md`
- `.agents/skills/create-component/details/implementation-steps.md`
- `.agents/skills/create-component/details/verification-checklist.md`
- `packages/css/AGENTS.md`
- `packages/qvism-preset/AGENTS.md`
- `packages/react/AGENTS.md`
- `skills/create-component/SKILL.md`
- `skills/create-component/references/implementation-steps.md`
- `skills/create-component/references/verification-checklist.md`

## What to add / change

AGENTS.md 가이드라인 추가 및 create-component 스킬 문서 업데이트 내용을 image-frame PR에서 분리했습니다.

## Changes
- `packages/css/AGENTS.md`: defineRecipe vs defineSlotRecipe 차이 설명 추가
- `packages/qvism-preset/AGENTS.md`: recipe 스타일 작성 가이드라인 추가
- `packages/react/AGENTS.md`: React 컴포넌트 개발 가이드라인 추가
- `.agents/skills/create-component/details/`: implementation-steps, verification-checklist 추가
- `skills/create-component/references/`: 동일 내용 동기화

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **문서화**
  * SlotRecipe 기반 복합 컴포넌트 패턴에 대한 상세 가이드 추가(개념·사용법·마이그레이션 주의사항).
  * 코드 예제를 서술형 지침으로 대체하여 Headless 훅, 레시피(defineRecipe vs defineSlotRecipe), 슬롯·스니펫 레이어 사용 흐름을 명확화.
  * 레지스트리·예제 위치 및 임포트 경로 규칙, CSS 클래스명 변경(.seed-{name} → .seed-{name}__root), 생성 명령 실행 필요성 명시.
  * 검증 체크리스트 확대(일반 오류, 실행 순서, Visual Test 요구사항, React 패턴 금지사항).
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).

"""Behavioral checks for seed-design-docs-add-splitvariantprops-convention-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/seed-design")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-component/SKILL.md')
    assert '5. 상세 구현은 `details/implementation-steps.md`와 `details/verification-checklist.md`를 사용합니다.' in text, "expected to find: " + '5. 상세 구현은 `details/implementation-steps.md`와 `details/verification-checklist.md`를 사용합니다.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-component/SKILL.md')
    assert '4. `bun packages:build`, `bun typecheck`, Visual Test 체크리스트를 완료합니다.' in text, "expected to find: " + '4. `bun packages:build`, `bun typecheck`, Visual Test 체크리스트를 완료합니다.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-component/SKILL.md')
    assert '1. 각 단계에서 수정 대상 폴더의 `AGENTS.md`를 먼저 읽고 해당 패키지의 컨벤션을 확인합니다.' in text, "expected to find: " + '1. 각 단계에서 수정 대상 폴더의 `AGENTS.md`를 먼저 읽고 해당 패키지의 컨벤션을 확인합니다.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-component/details/implementation-steps.md')
    assert 'variant props(`variant`, `size`, `tone` 등)는 함수 인자에서 수동 destructuring하지 않는다. 반드시 `recipe.splitVariantProps(props)`를 사용하거나, `createRecipeContext`/`createSlotRecipeContext` 유틸을 사용한다. 세 패턴 모두 내부적으로 `split' in text, "expected to find: " + 'variant props(`variant`, `size`, `tone` 등)는 함수 인자에서 수동 destructuring하지 않는다. 반드시 `recipe.splitVariantProps(props)`를 사용하거나, `createRecipeContext`/`createSlotRecipeContext` 유틸을 사용한다. 세 패턴 모두 내부적으로 `split'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-component/details/implementation-steps.md')
    assert '1. **variant props 수동 destructuring**: `recipe.splitVariantProps(props)` 또는 `createRecipeContext`/`createSlotRecipeContext`를 사용한다. `({ variant, size, ...rest })` 형태 금지.' in text, "expected to find: " + '1. **variant props 수동 destructuring**: `recipe.splitVariantProps(props)` 또는 `createRecipeContext`/`createSlotRecipeContext`를 사용한다. `({ variant, size, ...rest })` 형태 금지.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-component/details/implementation-steps.md')
    assert '⚠️ **금지 패턴**: `({ variant, size, ...rest })` 형태로 variant를 함수 인자에서 직접 꺼내거나, `recipe({ variant, size })` 형태로 직접 전달하면 안 된다. variant가 추가/변경될 때 누락 위험이 있고, 타입 안전성이 보장되지 않는다.' in text, "expected to find: " + '⚠️ **금지 패턴**: `({ variant, size, ...rest })` 형태로 variant를 함수 인자에서 직접 꺼내거나, `recipe({ variant, size })` 형태로 직접 전달하면 안 된다. variant가 추가/변경될 때 누락 위험이 있고, 타입 안전성이 보장되지 않는다.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/react/AGENTS.md')
    assert 'context 유틸 없이 컴포넌트 내부에서 `recipe.splitVariantProps(props)`를 직접 호출하여 `[variantProps, restProps]` 튜플로 분리한다. 반환된 `variantProps`만 recipe 함수에 전달하고, `restProps`는 DOM 요소에 spread한다. Badge 컴포넌트가 대표적인 예시이다.' in text, "expected to find: " + 'context 유틸 없이 컴포넌트 내부에서 `recipe.splitVariantProps(props)`를 직접 호출하여 `[variantProps, restProps]` 튜플로 분리한다. 반환된 `variantProps`만 recipe 함수에 전달하고, `restProps`는 DOM 요소에 spread한다. Badge 컴포넌트가 대표적인 예시이다.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/react/AGENTS.md')
    assert '- variant props(`variant`, `size`, `tone` 등)는 함수 인자에서 수동 destructuring 금지. 반드시 `recipe.splitVariantProps(props)` 또는 `createRecipeContext`/`createSlotRecipeContext` 유틸을 사용한다.' in text, "expected to find: " + '- variant props(`variant`, `size`, `tone` 등)는 함수 인자에서 수동 destructuring 금지. 반드시 `recipe.splitVariantProps(props)` 또는 `createRecipeContext`/`createSlotRecipeContext` 유틸을 사용한다.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/react/AGENTS.md')
    assert '`createSlotRecipeContext(slotRecipe)`로 context를 생성하고, `withProvider`로 Root를, `withContext`로 하위 슬롯을 연결한다. 내부에서 자동으로 `splitVariantProps`를 호출한다. Chip 컴포넌트가 대표적인 예시이다.' in text, "expected to find: " + '`createSlotRecipeContext(slotRecipe)`로 context를 생성하고, `withProvider`로 Root를, `withContext`로 하위 슬롯을 연결한다. 내부에서 자동으로 `splitVariantProps`를 호출한다. Chip 컴포넌트가 대표적인 예시이다.'[:80]


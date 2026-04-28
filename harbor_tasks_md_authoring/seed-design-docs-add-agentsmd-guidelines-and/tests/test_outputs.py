"""Behavioral checks for seed-design-docs-add-agentsmd-guidelines-and (markdown_authoring task).

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
    assert 'Snippet 파일은 `"use client"` 선언으로 시작하며, `@seed-design/react`에서 compound 컴포넌트를 import하여 단순화된 API로 래핑한다. Props 인터페이스는 `SeedComponentName.RootProps`를 extends하고, `src`, `alt`, `fallback` 같은 편의 prop을 추가한다. 반' in text, "expected to find: " + 'Snippet 파일은 `"use client"` 선언으로 시작하며, `@seed-design/react`에서 compound 컴포넌트를 import하여 단순화된 API로 래핑한다. Props 인터페이스는 `SeedComponentName.RootProps`를 extends하고, `src`, `alt`, `fallback` 같은 편의 prop을 추가한다. 반'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-component/details/implementation-steps.md')
    assert 'Recipe 파일에서 `../vars/component/`의 생성된 토큰을 import하고, `defineRecipe` 또는 `defineSlotRecipe`로 스타일을 정의한다. 어떤 함수를 사용할지, 슬롯 구조, 전환 시 주의사항은 `packages/qvism-preset/AGENTS.md`에 명시되어 있다.' in text, "expected to find: " + 'Recipe 파일에서 `../vars/component/`의 생성된 토큰을 import하고, `defineRecipe` 또는 `defineSlotRecipe`로 스타일을 정의한다. 어떤 함수를 사용할지, 슬롯 구조, 전환 시 주의사항은 `packages/qvism-preset/AGENTS.md`에 명시되어 있다.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-component/details/implementation-steps.md')
    assert 'Snippet 레이어가 있는 경우 `seed-design/ui/[name]`에서 import하고, Layout 컴포넌트(Flex, VStack 등)는 `@seed-design/react`에서 import한다. Snippet 레이어가 없는 경우 `@seed-design/react`에서 직접 import한다.' in text, "expected to find: " + 'Snippet 레이어가 있는 경우 `seed-design/ui/[name]`에서 import하고, Layout 컴포넌트(Flex, VStack 등)는 `@seed-design/react`에서 import한다. Snippet 레이어가 없는 경우 `@seed-design/react`에서 직접 import한다.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-component/details/verification-checklist.md')
    assert 'Recipe 타입을 변경하거나 슬롯을 추가한 후에는 반드시 `bun generate:all`을 먼저 실행한 뒤 React 코드를 수정한다. 상세는 `packages/qvism-preset/AGENTS.md`와 `packages/css/AGENTS.md` 참조.' in text, "expected to find: " + 'Recipe 타입을 변경하거나 슬롯을 추가한 후에는 반드시 `bun generate:all`을 먼저 실행한 뒤 React 코드를 수정한다. 상세는 `packages/qvism-preset/AGENTS.md`와 `packages/css/AGENTS.md` 참조.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-component/details/verification-checklist.md')
    assert 'variant props 수동 destructuring, 잘못된 import 경로, style prop 직접 사용 등의 금지 패턴은 `packages/react/AGENTS.md`에 명시되어 있다. 구현 전 반드시 확인한다.' in text, "expected to find: " + 'variant props 수동 destructuring, 잘못된 import 경로, style prop 직접 사용 등의 금지 패턴은 `packages/react/AGENTS.md`에 명시되어 있다. 구현 전 반드시 확인한다.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-component/details/verification-checklist.md')
    assert '반드시 Rootage → generate → Recipe → React → Docs → Test 순서를 따른다. React를 먼저 작성하면 CSS 변수가 없어서 스타일이 깨진다.' in text, "expected to find: " + '반드시 Rootage → generate → Recipe → React → Docs → Test 순서를 따른다. React를 먼저 작성하면 CSS 변수가 없어서 스타일이 깨진다.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/css/AGENTS.md')
    assert '| `packages/rootage/components/*.yaml` | `bun rootage:generate` | `packages/css/vars/component/*.{mjs,d.ts}` |' in text, "expected to find: " + '| `packages/rootage/components/*.yaml` | `bun rootage:generate` | `packages/css/vars/component/*.{mjs,d.ts}` |'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/css/AGENTS.md')
    assert '| `packages/qvism-preset/src/recipes/*.ts` | `bun qvism:generate` | `packages/css/recipes/*.{css,mjs,d.ts}` |' in text, "expected to find: " + '| `packages/qvism-preset/src/recipes/*.ts` | `bun qvism:generate` | `packages/css/recipes/*.{css,mjs,d.ts}` |'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/css/AGENTS.md')
    assert '| `defineSlotRecipe` | `.seed-{name}__{slot}` | `.seed-avatar__root`, `.seed-avatar__fallback` |' in text, "expected to find: " + '| `defineSlotRecipe` | `.seed-{name}__{slot}` | `.seed-avatar__root`, `.seed-avatar__fallback` |'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/qvism-preset/AGENTS.md')
    assert '`defineSlotRecipe`는 `name`, `slots` 배열, `base`, `variants` 등을 인자로 받는다. `base.slotName` 형태로 슬롯별 기본 스타일을 작성하고, `variants.variantName.variantValue.slotName` 형태로 슬롯별 variants를 적용한다.' in text, "expected to find: " + '`defineSlotRecipe`는 `name`, `slots` 배열, `base`, `variants` 등을 인자로 받는다. `base.slotName` 형태로 슬롯별 기본 스타일을 작성하고, `variants.variantName.variantValue.slotName` 형태로 슬롯별 variants를 적용한다.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/qvism-preset/AGENTS.md')
    assert '2. **CSS 클래스명 패턴이 변경됨**: `defineRecipe`의 `.seed-{name}` → `defineSlotRecipe`의 `.seed-{name}__root`로 변경되므로 React 컴포넌트에서 사용하는 import도 업데이트 필요.' in text, "expected to find: " + '2. **CSS 클래스명 패턴이 변경됨**: `defineRecipe`의 `.seed-{name}` → `defineSlotRecipe`의 `.seed-{name}__root`로 변경되므로 React 컴포넌트에서 사용하는 import도 업데이트 필요.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/qvism-preset/AGENTS.md')
    assert '1. **반드시 `bun generate:all` 실행**: Recipe 타입을 변경한 후 generate를 실행하지 않으면 CSS와 소스가 불일치해 빌드가 깨집니다.' in text, "expected to find: " + '1. **반드시 `bun generate:all` 실행**: Recipe 타입을 변경한 후 generate를 실행하지 않으면 CSS와 소스가 불일치해 빌드가 깨집니다.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/react/AGENTS.md')
    assert 'context 유틸 없이 컴포넌트 내부에서 `recipe.splitVariantProps(props)`를 직접 호출하여 `[variantProps, restProps]` 튜플로 분리한다. 반환된 `variantProps`만 recipe 함수에 전달하고, `restProps`는 DOM 요소에 spread한다. Badge 컴포넌트가 대표적인 예시이다.' in text, "expected to find: " + 'context 유틸 없이 컴포넌트 내부에서 `recipe.splitVariantProps(props)`를 직접 호출하여 `[variantProps, restProps]` 튜플로 분리한다. 반환된 `variantProps`만 recipe 함수에 전달하고, `restProps`는 DOM 요소에 spread한다. Badge 컴포넌트가 대표적인 예시이다.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/react/AGENTS.md')
    assert '스타일은 반드시 qvism-preset recipe를 통해 className으로 적용해야 한다. style prop을 직접 사용하면 테마, 다크모드, CSS 변수 활용이 불가능하고 스타일 관리가 분산된다. 해당 슬롯의 스타일은 qvism-preset recipe의 `base.slotName`에 작성하고, `withContext`로 연결한다.' in text, "expected to find: " + '스타일은 반드시 qvism-preset recipe를 통해 className으로 적용해야 한다. style prop을 직접 사용하면 테마, 다크모드, CSS 변수 활용이 불가능하고 스타일 관리가 분산된다. 해당 슬롯의 스타일은 qvism-preset recipe의 `base.slotName`에 작성하고, `withContext`로 연결한다.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/react/AGENTS.md')
    assert '- variant props(`variant`, `size`, `tone` 등)는 함수 인자에서 수동 destructuring 금지. 반드시 `recipe.splitVariantProps(props)` 또는 `createRecipeContext`/`createSlotRecipeContext` 유틸을 사용한다.' in text, "expected to find: " + '- variant props(`variant`, `size`, `tone` 등)는 함수 인자에서 수동 destructuring 금지. 반드시 `recipe.splitVariantProps(props)` 또는 `createRecipeContext`/`createSlotRecipeContext` 유틸을 사용한다.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-component/SKILL.md')
    assert '1. 각 단계에서 수정 대상 폴더의 `AGENTS.md`를 먼저 읽고 해당 패키지의 컨벤션을 확인한다.' in text, "expected to find: " + '1. 각 단계에서 수정 대상 폴더의 `AGENTS.md`를 먼저 읽고 해당 패키지의 컨벤션을 확인한다.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-component/SKILL.md')
    assert '3. `references/`에서 현재 작업에 필요한 문서만 읽는다.' in text, "expected to find: " + '3. `references/`에서 현재 작업에 필요한 문서만 읽는다.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-component/SKILL.md')
    assert '2. 대상 범위와 목표 결과를 먼저 확정한다.' in text, "expected to find: " + '2. 대상 범위와 목표 결과를 먼저 확정한다.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-component/references/implementation-steps.md')
    assert 'Snippet 파일은 `"use client"` 선언으로 시작하며, `@seed-design/react`에서 compound 컴포넌트를 import하여 단순화된 API로 래핑한다. Props 인터페이스는 `SeedComponentName.RootProps`를 extends하고, `src`, `alt`, `fallback` 같은 편의 prop을 추가한다. 반' in text, "expected to find: " + 'Snippet 파일은 `"use client"` 선언으로 시작하며, `@seed-design/react`에서 compound 컴포넌트를 import하여 단순화된 API로 래핑한다. Props 인터페이스는 `SeedComponentName.RootProps`를 extends하고, `src`, `alt`, `fallback` 같은 편의 prop을 추가한다. 반'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-component/references/implementation-steps.md')
    assert 'Recipe 파일에서 `../vars/component/`의 생성된 토큰을 import하고, `defineRecipe` 또는 `defineSlotRecipe`로 스타일을 정의한다. 어떤 함수를 사용할지, 슬롯 구조, 전환 시 주의사항은 `packages/qvism-preset/AGENTS.md`에 명시되어 있다.' in text, "expected to find: " + 'Recipe 파일에서 `../vars/component/`의 생성된 토큰을 import하고, `defineRecipe` 또는 `defineSlotRecipe`로 스타일을 정의한다. 어떤 함수를 사용할지, 슬롯 구조, 전환 시 주의사항은 `packages/qvism-preset/AGENTS.md`에 명시되어 있다.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-component/references/implementation-steps.md')
    assert 'Snippet 레이어가 있는 경우 `seed-design/ui/[name]`에서 import하고, Layout 컴포넌트(Flex, VStack 등)는 `@seed-design/react`에서 import한다. Snippet 레이어가 없는 경우 `@seed-design/react`에서 직접 import한다.' in text, "expected to find: " + 'Snippet 레이어가 있는 경우 `seed-design/ui/[name]`에서 import하고, Layout 컴포넌트(Flex, VStack 등)는 `@seed-design/react`에서 import한다. Snippet 레이어가 없는 경우 `@seed-design/react`에서 직접 import한다.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-component/references/verification-checklist.md')
    assert 'Recipe 타입을 변경하거나 슬롯을 추가한 후에는 반드시 `bun generate:all`을 먼저 실행한 뒤 React 코드를 수정한다. 상세는 `packages/qvism-preset/AGENTS.md`와 `packages/css/AGENTS.md` 참조.' in text, "expected to find: " + 'Recipe 타입을 변경하거나 슬롯을 추가한 후에는 반드시 `bun generate:all`을 먼저 실행한 뒤 React 코드를 수정한다. 상세는 `packages/qvism-preset/AGENTS.md`와 `packages/css/AGENTS.md` 참조.'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-component/references/verification-checklist.md')
    assert 'variant props 수동 destructuring, 잘못된 import 경로, style prop 직접 사용 등의 금지 패턴은 `packages/react/AGENTS.md`에 명시되어 있다. 구현 전 반드시 확인한다.' in text, "expected to find: " + 'variant props 수동 destructuring, 잘못된 import 경로, style prop 직접 사용 등의 금지 패턴은 `packages/react/AGENTS.md`에 명시되어 있다. 구현 전 반드시 확인한다.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-component/references/verification-checklist.md')
    assert '반드시 Rootage → generate → Recipe → React → Docs → Test 순서를 따른다. React를 먼저 작성하면 CSS 변수가 없어서 스타일이 깨진다.' in text, "expected to find: " + '반드시 Rootage → generate → Recipe → React → Docs → Test 순서를 따른다. React를 먼저 작성하면 CSS 변수가 없어서 스타일이 깨진다.'[:80]


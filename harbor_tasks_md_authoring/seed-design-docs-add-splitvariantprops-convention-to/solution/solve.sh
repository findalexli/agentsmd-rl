#!/usr/bin/env bash
set -euo pipefail

cd /workspace/seed-design

# Idempotency guard
if grep -qF "5. \uc0c1\uc138 \uad6c\ud604\uc740 `details/implementation-steps.md`\uc640 `details/verification-checklist.md`" ".agents/skills/create-component/SKILL.md" && grep -qF "variant props(`variant`, `size`, `tone` \ub4f1)\ub294 \ud568\uc218 \uc778\uc790\uc5d0\uc11c \uc218\ub3d9 destructuring\ud558\uc9c0 \uc54a\ub294\ub2e4. \ubc18\ub4dc\uc2dc " ".agents/skills/create-component/details/implementation-steps.md" && grep -qF "context \uc720\ud2f8 \uc5c6\uc774 \ucef4\ud3ec\ub10c\ud2b8 \ub0b4\ubd80\uc5d0\uc11c `recipe.splitVariantProps(props)`\ub97c \uc9c1\uc811 \ud638\ucd9c\ud558\uc5ec `[variantProp" "packages/react/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/create-component/SKILL.md b/.agents/skills/create-component/SKILL.md
@@ -9,10 +9,11 @@ description: End-to-end SEED component implementation guide from rootage spec to
 
 ## Quick Start
 
-1. Rootage 스펙을 정의/수정하고 `bun generate:all`을 실행합니다.
-2. Recipe, React UI, Storybook, 문서를 순서대로 반영합니다.
-3. `bun packages:build`, `bun typecheck`, Visual Test 체크리스트를 완료합니다.
-4. 상세 구현은 `details/implementation-steps.md`와 `details/verification-checklist.md`를 사용합니다.
+1. 각 단계에서 수정 대상 폴더의 `AGENTS.md`를 먼저 읽고 해당 패키지의 컨벤션을 확인합니다.
+2. Rootage 스펙을 정의/수정하고 `bun generate:all`을 실행합니다.
+3. Recipe, React UI, Storybook, 문서를 순서대로 반영합니다.
+4. `bun packages:build`, `bun typecheck`, Visual Test 체크리스트를 완료합니다.
+5. 상세 구현은 `details/implementation-steps.md`와 `details/verification-checklist.md`를 사용합니다.
 
 ## 핵심 흐름
 
diff --git a/.agents/skills/create-component/details/implementation-steps.md b/.agents/skills/create-component/details/implementation-steps.md
@@ -18,6 +18,7 @@ YAML 파일에 `id`(kebab-case), `name`, `description`을 정의하고, `slots`
 
 **위치**: `packages/qvism-preset/src/recipes/[name].ts`
 **추가 작업**: `recipes/index.ts`에 export 추가
+**컨벤션**: 구현 전 `packages/qvism-preset/AGENTS.md`를 읽고 해당 패키지의 컨벤션을 확인한다.
 
 Recipe 파일에서 `../vars/component/`의 생성된 토큰을 import하고, `defineRecipe`로 `base`, `variants`, `defaultVariants`를 정의한다.
 
@@ -37,25 +38,38 @@ Recipe 파일에서 `../vars/component/`의 생성된 토큰을 import하고, `d
 
 **위치**: `packages/react/src/components/[ComponentName]/`
 **빌드**: 완료 후 `bun packages:build`
+**컨벤션**: 구현 전 `packages/react/AGENTS.md`를 읽고 해당 패키지의 컨벤션을 확인한다.
 
 ### 아키텍처 패턴
 
 | 유형 | 패턴 | 예시 |
 |------|------|------|
-| 단일 컴포넌트 | `createRecipeContext` | Button, Badge |
-| 복합 컴포넌트 | `createSlotRecipeContext` | TextField, Chip |
+| 직접 splitVariantProps | `recipe.splitVariantProps(props)` | Badge |
+| 단일 슬롯 | `createRecipeContext` → `withContext` | Fab |
+| 복합 슬롯 | `createSlotRecipeContext` → `withProvider`/`withContext` | Chip |
 
-단일 컴포넌트는 Headless 컴포넌트와 CSS recipe를 import하여 `forwardRef`로 감싸고, recipe 함수 호출 결과를 className에 적용한다. 반드시 `displayName`을 설정한다.
+### Variant Props 처리 (필수)
+
+variant props(`variant`, `size`, `tone` 등)는 함수 인자에서 수동 destructuring하지 않는다. 반드시 `recipe.splitVariantProps(props)`를 사용하거나, `createRecipeContext`/`createSlotRecipeContext` 유틸을 사용한다. 세 패턴 모두 내부적으로 `splitVariantProps`를 호출하여 variant props와 HTML 속성을 타입 안전하게 분리한다.
+
+`recipe.splitVariantProps(props)`는 `[variantProps, restProps]` 튜플을 반환한다. `variantProps`만 recipe 함수에 전달하고, `restProps`는 DOM 요소에 spread한다.
+
+⚠️ **금지 패턴**: `({ variant, size, ...rest })` 형태로 variant를 함수 인자에서 직접 꺼내거나, `recipe({ variant, size })` 형태로 직접 전달하면 안 된다. variant가 추가/변경될 때 누락 위험이 있고, 타입 안전성이 보장되지 않는다.
+
+### 단일 슬롯 패턴 (createRecipeContext)
+
+`createRecipeContext(recipe)`로 context를 생성하고, `withContext`로 Primitive 요소를 감싸면 내부에서 자동으로 `splitVariantProps`를 호출한다. `forwardRef`로 감싸고 반드시 `displayName`을 설정한다.
 
 ### SlotRecipe 기반 복합 컴포넌트 패턴
 
 슬롯 recipe를 사용하는 경우 `createSlotRecipeContext`를 활용한다. `createSlotRecipeContext`는 반드시 `../../utils/createSlotRecipeContext` 상대 경로에서 import하고, slotRecipe 함수를 직접 전달한다. `withProvider`로 Root 컴포넌트를, `withContext`로 하위 슬롯 컴포넌트를 연결하면 각 슬롯에 자동으로 해당 className이 적용된다.
 
 **⚠️ 흔한 실수들**:
 
-1. **존재하지 않는 패키지 import**: `createSlotRecipeContext`는 `@seed-design/react-utils`가 아닌 `../../utils/createSlotRecipeContext` 상대 경로에서 import한다.
-2. **잘못된 createSlotRecipeContext 호출**: slotRecipe를 객체로 감싸지 말고 직접 전달한다.
-3. **React 레이어에 style 직접 작성**: style prop 대신 qvism-preset recipe의 해당 슬롯에 스타일을 작성하고, `withContext`로 연결한다.
+1. **variant props 수동 destructuring**: `recipe.splitVariantProps(props)` 또는 `createRecipeContext`/`createSlotRecipeContext`를 사용한다. `({ variant, size, ...rest })` 형태 금지.
+2. **존재하지 않는 패키지 import**: `createSlotRecipeContext`는 `@seed-design/react-utils`가 아닌 `../../utils/createSlotRecipeContext` 상대 경로에서 import한다.
+3. **잘못된 createSlotRecipeContext 호출**: slotRecipe를 객체로 감싸지 말고 직접 전달한다.
+4. **React 레이어에 style 직접 작성**: style prop 대신 qvism-preset recipe의 해당 슬롯에 스타일을 작성하고, `withContext`로 연결한다.
 
 ## Step 5: Registry UI (Snippet 레이어)
 
diff --git a/packages/react/AGENTS.md b/packages/react/AGENTS.md
@@ -18,11 +18,38 @@
 - `clsx`로 className 병합
 - HTML 요소 대신 `Primitive.*` 사용
 - compound component의 경우 Root 컴포넌트가 context를 포함해야 하고 하위 컴포넌트가 상위 context에서 제공하는 값을 바탕으로 동작해야 하므로 `createSlotRecipeContext`가 제공하는 도구를 적극적으로 활용한다.
+- variant props(`variant`, `size`, `tone` 등)는 함수 인자에서 수동 destructuring 금지. 반드시 `recipe.splitVariantProps(props)` 또는 `createRecipeContext`/`createSlotRecipeContext` 유틸을 사용한다.
 
 ## 코드 스타일
 
 모든 컴포넌트는 반드시 `forwardRef`로 감싸고 `displayName`을 설정해야 한다. HTML 요소 대신 `Primitive.*`을 사용하고, Recipe 함수 호출 결과를 `clsx`로 className에 병합한다.
 
+## Variant Props 처리 패턴
+
+variant props는 반드시 아래 세 가지 패턴 중 하나로 처리한다. 세 패턴 모두 내부적으로 `splitVariantProps`를 사용하여 variant props와 HTML 속성을 타입 안전하게 분리한다.
+
+| 유형 | 도구 | 예시 |
+|------|------|------|
+| 직접 splitVariantProps | `recipe.splitVariantProps(props)` | Badge |
+| 단일 슬롯 | `createRecipeContext` → `withContext` | Fab |
+| 복합 슬롯 | `createSlotRecipeContext` → `withProvider`/`withContext` | Chip |
+
+### 직접 splitVariantProps
+
+context 유틸 없이 컴포넌트 내부에서 `recipe.splitVariantProps(props)`를 직접 호출하여 `[variantProps, restProps]` 튜플로 분리한다. 반환된 `variantProps`만 recipe 함수에 전달하고, `restProps`는 DOM 요소에 spread한다. Badge 컴포넌트가 대표적인 예시이다.
+
+### createRecipeContext (단일 슬롯)
+
+`createRecipeContext(recipe)`로 context를 생성하고, `withContext`로 Primitive 요소를 감싸면 내부에서 자동으로 `splitVariantProps`를 호출한다. Fab 컴포넌트가 대표적인 예시이다.
+
+### createSlotRecipeContext (복합 슬롯)
+
+`createSlotRecipeContext(slotRecipe)`로 context를 생성하고, `withProvider`로 Root를, `withContext`로 하위 슬롯을 연결한다. 내부에서 자동으로 `splitVariantProps`를 호출한다. Chip 컴포넌트가 대표적인 예시이다.
+
+### 절대 금지: variant props 수동 destructuring
+
+`({ variant, size, ...rest })` 형태로 variant를 함수 인자에서 직접 꺼내거나, `recipe({ variant, size })` 형태로 직접 전달하면 안 된다. variant가 추가/변경될 때 누락 위험이 있고, 타입 안전성이 보장되지 않는다.
+
 ## SlotRecipe 사용 패턴
 
 복합 컴포넌트(슬롯이 여러 개인 경우)는 `createSlotRecipeContext`를 사용한다.
PATCH

echo "Gold patch applied."

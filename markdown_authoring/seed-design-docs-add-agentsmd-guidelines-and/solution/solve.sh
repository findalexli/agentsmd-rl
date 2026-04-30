#!/usr/bin/env bash
set -euo pipefail

cd /workspace/seed-design

# Idempotency guard
if grep -qF "5. \uc0c1\uc138 \uad6c\ud604\uc740 `details/implementation-steps.md`\uc640 `details/verification-checklist.md`" ".agents/skills/create-component/SKILL.md" && grep -qF "Snippet \ud30c\uc77c\uc740 `\"use client\"` \uc120\uc5b8\uc73c\ub85c \uc2dc\uc791\ud558\uba70, `@seed-design/react`\uc5d0\uc11c compound \ucef4\ud3ec\ub10c\ud2b8\ub97c impo" ".agents/skills/create-component/details/implementation-steps.md" && grep -qF "Recipe \ud0c0\uc785\uc744 \ubcc0\uacbd\ud558\uac70\ub098 \uc2ac\ub86f\uc744 \ucd94\uac00\ud55c \ud6c4\uc5d0\ub294 \ubc18\ub4dc\uc2dc `bun generate:all`\uc744 \uba3c\uc800 \uc2e4\ud589\ud55c \ub4a4 React \ucf54\ub4dc\ub97c \uc218\uc815\ud55c\ub2e4. \uc0c1\uc138" ".agents/skills/create-component/details/verification-checklist.md" && grep -qF "| `packages/rootage/components/*.yaml` | `bun rootage:generate` | `packages/css/" "packages/css/AGENTS.md" && grep -qF "`defineSlotRecipe`\ub294 `name`, `slots` \ubc30\uc5f4, `base`, `variants` \ub4f1\uc744 \uc778\uc790\ub85c \ubc1b\ub294\ub2e4. `base.slo" "packages/qvism-preset/AGENTS.md" && grep -qF "context \uc720\ud2f8 \uc5c6\uc774 \ucef4\ud3ec\ub10c\ud2b8 \ub0b4\ubd80\uc5d0\uc11c `recipe.splitVariantProps(props)`\ub97c \uc9c1\uc811 \ud638\ucd9c\ud558\uc5ec `[variantProp" "packages/react/AGENTS.md" && grep -qF "1. \uac01 \ub2e8\uacc4\uc5d0\uc11c \uc218\uc815 \ub300\uc0c1 \ud3f4\ub354\uc758 `AGENTS.md`\ub97c \uba3c\uc800 \uc77d\uace0 \ud574\ub2f9 \ud328\ud0a4\uc9c0\uc758 \ucee8\ubca4\uc158\uc744 \ud655\uc778\ud55c\ub2e4." "skills/create-component/SKILL.md" && grep -qF "Snippet \ud30c\uc77c\uc740 `\"use client\"` \uc120\uc5b8\uc73c\ub85c \uc2dc\uc791\ud558\uba70, `@seed-design/react`\uc5d0\uc11c compound \ucef4\ud3ec\ub10c\ud2b8\ub97c impo" "skills/create-component/references/implementation-steps.md" && grep -qF "Recipe \ud0c0\uc785\uc744 \ubcc0\uacbd\ud558\uac70\ub098 \uc2ac\ub86f\uc744 \ucd94\uac00\ud55c \ud6c4\uc5d0\ub294 \ubc18\ub4dc\uc2dc `bun generate:all`\uc744 \uba3c\uc800 \uc2e4\ud589\ud55c \ub4a4 React \ucf54\ub4dc\ub97c \uc218\uc815\ud55c\ub2e4. \uc0c1\uc138" "skills/create-component/references/verification-checklist.md"; then
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
@@ -5,133 +5,70 @@
 **위치**: `packages/react-headless/[name]/`
 **조건**: 데이터 로직이 필요한 경우만 (단순 UI 컴포넌트는 생략)
 
-```typescript
-// use{Component}.ts
-export function useActionButton(props: UseActionButtonProps) {
-  const [pressed, setPressed] = useState(false)
-
-  return {
-    rootProps: {
-      'data-pressed': pressed,
-      'data-disabled': props.disabled,
-      onPointerDown: handlePointerDown,
-      onClick: props.onClick,
-    },
-  }
-}
-```
+Headless 훅은 `use{Component}.ts` 파일에 `use{Component}` 형태로 작성한다. 훅은 `data-pressed`, `data-disabled` 같은 data 속성과 이벤트 핸들러(`onPointerDown`, `onClick` 등)를 `rootProps` 객체로 반환한다.
 
 ## Step 2: Definition (Rootage)
 
 **위치**: `packages/rootage/components/[name].yaml`
 **명령어**: 완료 후 `bun generate:all`
 
-```yaml
-# [component-name].yaml
-id: action-button
-name: Action Button
-description: 사용자 액션을 트리거하는 버튼
-
-slots:
-  root:
-    description: 버튼 루트 요소
-
-variants:
-  tone:
-    values: [neutral, brand, danger]
-    default: neutral
-  size:
-    values: [small, medium, large]
-    default: medium
-
-states:
-  - default
-  - hover
-  - pressed
-  - disabled
-```
+`packages/rootage/components/schema.json`을 참고하여 YAML 파일을 작성한다. 스키마에 정의된 `kind`, `metadata`, `data` 구조를 따르며, slots/variants/definitions를 올바르게 구성한다.
 
 ## Step 3: Recipe (Qvism Preset)
 
 **위치**: `packages/qvism-preset/src/recipes/[name].ts`
 **추가 작업**: `recipes/index.ts`에 export 추가
+**컨벤션**: 구현 전 `packages/qvism-preset/AGENTS.md`를 읽고 해당 패키지의 컨벤션을 확인한다.
 
-```typescript
-import { defineRecipe } from "@seed-design/qvism"
-import { actionButton } from "../vars/component/action-button"
-
-export const actionButtonRecipe = defineRecipe({
-  base: actionButton.root,
-  variants: {
-    tone: {
-      neutral: { /* ... */ },
-      brand: { /* ... */ },
-    },
-    size: {
-      small: { /* ... */ },
-      medium: { /* ... */ },
-    },
-  },
-  defaultVariants: {
-    tone: "neutral",
-    size: "medium",
-  },
-})
-```
+Recipe 파일에서 `../vars/component/`의 생성된 토큰을 import하고, `defineRecipe` 또는 `defineSlotRecipe`로 스타일을 정의한다. 어떤 함수를 사용할지, 슬롯 구조, 전환 시 주의사항은 `packages/qvism-preset/AGENTS.md`에 명시되어 있다.
 
 **주의**: hover 대신 active 상태 사용 (모바일 우선)
 
 ## Step 4: React 컴포넌트
 
 **위치**: `packages/react/src/components/[ComponentName]/`
 **빌드**: 완료 후 `bun packages:build`
+**컨벤션**: 구현 전 `packages/react/AGENTS.md`를 읽고 해당 패키지의 컨벤션을 확인한다.
 
-### 아키텍처 패턴
-
-| 유형 | 패턴 | 예시 |
-|------|------|------|
-| 단일 컴포넌트 | `createRecipeContext` | Button, Badge |
-| 복합 컴포넌트 | `createSlotRecipeContext` | TextField, Chip |
-
-```typescript
-import { ActionButton as HeadlessActionButton } from '@seed-design/react-headless'
-import { actionButton } from '@seed-design/css/components/action-button'
-
-export const ActionButton = forwardRef<HTMLButtonElement, ActionButtonProps>(
-  ({ tone = 'neutral', size = 'medium', ...props }, ref) => {
-    return (
-      <HeadlessActionButton
-        ref={ref}
-        className={actionButton({ tone, size })}
-        {...props}
-      />
-    )
-  }
-)
-ActionButton.displayName = "ActionButton"
-```
-
-## Step 5: Registry UI (선택)
+Variant Props 처리 패턴, 단일/복합 슬롯 패턴, 금지 패턴 등의 상세는 `packages/react/AGENTS.md`에 명시되어 있다.
+
+## Step 5: Registry UI (Snippet 레이어)
 
 **위치**: `docs/registry/ui/[name].tsx`
-**조건**: 복합 컴포넌트의 경우
+
+### Snippet 레이어가 필요한 경우
+
+다음 조건 중 하나라도 해당하면 snippet 레이어를 추가해야 합니다:
+1. **복합 컴포넌트**: Root+Content+Fallback 등 여러 서브컴포넌트를 조합해야 하는 경우 (Avatar, ImageFrame 등)
+2. **서드파티 의존성 통합**: 외부 아이콘 라이브러리나 다른 패키지를 함께 사용해야 하는 경우
+3. **보일러플레이트 단순화**: 사용자가 매번 직접 조합하면 너무 복잡한 경우 (Image.Root + Image.Fallback + Image.Content 등)
+
+### 반대로 Snippet이 필요 없는 경우
+
+- 단일 컴포넌트 (`<Button>`, `<Badge>` 등): `@seed-design/react`에서 직접 사용
+- 이미 심플한 API를 가진 경우
+
+### Snippet 파일 작성 패턴
+
+Snippet 파일은 `"use client"` 선언으로 시작하며, `@seed-design/react`에서 compound 컴포넌트를 import하여 단순화된 API로 래핑한다. Props 인터페이스는 `SeedComponentName.RootProps`를 extends하고, `src`, `alt`, `fallback` 같은 편의 prop을 추가한다. 반드시 `React.forwardRef`로 감싸고 `displayName`을 설정한다. 하위 컴포넌트가 있으면 별도 인터페이스와 함께 re-export한다.
 
 **추가 작업**:
-1. `docs/registry/registry-ui.ts`에 entry 추가
+1. `docs/registry/registry-ui.ts`에 entry 추가 (의존성 버전은 해당 컴포넌트가 추가된 버전 기준)
 2. `bun --filter @seed-design/docs generate:registry` 실행
 
-## Step 6: Examples
+### React 문서 업데이트
 
-**위치**: `docs/components/example/[name]-*.tsx`
+Snippet 레이어가 있는 컴포넌트의 문서는 반드시 다음 형태로 업데이트해야 합니다:
+- `## Installation` 섹션 추가: `npx @seed-design/cli@latest add ui:[name]` 명령어
+- `<ManualInstallation name="[name]" />` 컴포넌트 추가
+- `## Usage`의 import 경로를 `seed-design/ui/[name]`으로 변경
+- Props 섹션 경로를 `./registry/ui/[name].tsx`로 변경
+
+## Step 6: Examples
 
-```typescript
-// action-button-preview.tsx
-import { ActionButton } from "@seed-design/react"
+**위치**: `docs/examples/react/[name]/`
 
-export default function ActionButtonPreview() {
-  return <ActionButton>Click me</ActionButton>
-}
-```
+Snippet 레이어가 있는 경우 `seed-design/ui/[name]`에서 import하고, Layout 컴포넌트(Flex, VStack 등)는 `@seed-design/react`에서 import한다. Snippet 레이어가 없는 경우 `@seed-design/react`에서 직접 import한다.
 
 ## Step 7: Storybook
 
diff --git a/.agents/skills/create-component/details/verification-checklist.md b/.agents/skills/create-component/details/verification-checklist.md
@@ -17,30 +17,23 @@
 
 ### 잘못된 순서
 
-```text
-❌ React 먼저 → Rootage 나중에
-   → CSS 변수가 없어서 스타일 깨짐
-
-✅ Rootage → generate → Recipe → React → Docs → Test
-```
+반드시 Rootage → generate → Recipe → React → Docs → Test 순서를 따른다. React를 먼저 작성하면 CSS 변수가 없어서 스타일이 깨진다.
 
 ### Recipe export 누락
 
-```text
-❌ Recipe 작성 후 index.ts에 추가 안 함
-   → 컴포넌트에서 import 실패
-
-✅ recipes/index.ts에 반드시 export 추가
-```
+Recipe 작성 후 반드시 `recipes/index.ts`에 export를 추가해야 한다. 누락하면 컴포넌트에서 import가 실패한다.
 
 ### 테스트 생략
 
-```text
-❌ 구현만 하고 Visual Test 안 함
-   → 다크모드/폰트 스케일링 버그 발견 못함
+구현 후 반드시 Agent Browser로 Visual Test를 수행한다. 생략하면 다크모드나 폰트 스케일링 관련 버그를 발견하지 못한다.
+
+### Recipe-React 불일치
+
+Recipe 타입을 변경하거나 슬롯을 추가한 후에는 반드시 `bun generate:all`을 먼저 실행한 뒤 React 코드를 수정한다. 상세는 `packages/qvism-preset/AGENTS.md`와 `packages/css/AGENTS.md` 참조.
+
+### React 컴포넌트 패턴 위반
 
-✅ Agent Browser로 모든 환경 테스트
-```
+variant props 수동 destructuring, 잘못된 import 경로, style prop 직접 사용 등의 금지 패턴은 `packages/react/AGENTS.md`에 명시되어 있다. 구현 전 반드시 확인한다.
 
 ## 생성 파일 (수정 금지)
 
diff --git a/packages/css/AGENTS.md b/packages/css/AGENTS.md
@@ -19,3 +19,17 @@
 1. 토큰 → `packages/rootage/*.yaml` 수정
 2. Recipe → `packages/qvism-preset/src/recipes/*.ts` 수정
 3. `bun generate:all` 실행
+
+## 소스-생성물 관계
+
+| 소스 | 생성 명령 | 생성물 |
+|------|----------|--------|
+| `packages/qvism-preset/src/recipes/*.ts` | `bun qvism:generate` | `packages/css/recipes/*.{css,mjs,d.ts}` |
+| `packages/rootage/components/*.yaml` | `bun rootage:generate` | `packages/css/vars/component/*.{mjs,d.ts}` |
+
+## defineRecipe vs defineSlotRecipe 생성물 차이
+
+| Recipe 타입 | 클래스명 패턴 | 예시 |
+|------------|-------------|------|
+| `defineRecipe` | `.seed-{name}` | `.seed-button` |
+| `defineSlotRecipe` | `.seed-{name}__{slot}` | `.seed-avatar__root`, `.seed-avatar__fallback` |
diff --git a/packages/qvism-preset/AGENTS.md b/packages/qvism-preset/AGENTS.md
@@ -14,3 +14,21 @@
 - Recipe 이름: kebab-case (예: `action-button`)
 - Pseudo 선택자: `active` (hover 대신, 모바일 우선), `disabled`, `focus`, `checked` 등
 - 토큰 참조: `vars.{variant}.{state}.{slot}.{property}`
+
+## defineRecipe vs defineSlotRecipe
+
+| 기준 | `defineRecipe` | `defineSlotRecipe` |
+|------|---------------|-------------------|
+| 슬롯 수 | 1개 (root만) | 2개 이상 |
+| 예시 | ActionButton, Badge | Avatar, TextField, Chip |
+| CSS 클래스명 | `.seed-{name}` | `.seed-{name}__{slot}` |
+
+### defineSlotRecipe 사용법
+
+`defineSlotRecipe`는 `name`, `slots` 배열, `base`, `variants` 등을 인자로 받는다. `base.slotName` 형태로 슬롯별 기본 스타일을 작성하고, `variants.variantName.variantValue.slotName` 형태로 슬롯별 variants를 적용한다.
+
+### ⚠️ defineRecipe ↔ defineSlotRecipe 전환 시 주의사항
+
+1. **반드시 `bun generate:all` 실행**: Recipe 타입을 변경한 후 generate를 실행하지 않으면 CSS와 소스가 불일치해 빌드가 깨집니다.
+2. **CSS 클래스명 패턴이 변경됨**: `defineRecipe`의 `.seed-{name}` → `defineSlotRecipe`의 `.seed-{name}__root`로 변경되므로 React 컴포넌트에서 사용하는 import도 업데이트 필요.
+3. **올바른 순서**: Recipe 수정 → `bun generate:all` → React 코드 수정
diff --git a/packages/react/AGENTS.md b/packages/react/AGENTS.md
@@ -18,30 +18,54 @@
 - `clsx`로 className 병합
 - HTML 요소 대신 `Primitive.*` 사용
 - compound component의 경우 Root 컴포넌트가 context를 포함해야 하고 하위 컴포넌트가 상위 context에서 제공하는 값을 바탕으로 동작해야 하므로 `createSlotRecipeContext`가 제공하는 도구를 적극적으로 활용한다.
+- variant props(`variant`, `size`, `tone` 등)는 함수 인자에서 수동 destructuring 금지. 반드시 `recipe.splitVariantProps(props)` 또는 `createRecipeContext`/`createSlotRecipeContext` 유틸을 사용한다.
 
-## 코드 스타일 예시
-
-✅ Good:
-```tsx
-import { actionButton } from "@seed-design/css/recipes/action-button";
-import { Primitive } from "@seed-design/react-primitive";
-
-export const ActionButton = forwardRef<HTMLButtonElement, ActionButtonProps>(
-  ({ variant = "brandSolid", size = "medium", className, ...props }, ref) => (
-    <Primitive.button
-      ref={ref}
-      className={clsx(actionButton({ variant, size }), className)}
-      {...props}
-    />
-  )
-);
-ActionButton.displayName = "ActionButton";
-```
-
-❌ Bad:
-```tsx
-// forwardRef 누락, displayName 없음, Primitive 미사용
-export const ActionButton = (props) => (
-  <button className={actionButton(props)} {...props} />
-);
-```
+## 코드 스타일
+
+모든 컴포넌트는 반드시 `forwardRef`로 감싸고 `displayName`을 설정해야 한다. HTML 요소 대신 `Primitive.*`을 사용하고, Recipe 함수 호출 결과를 `clsx`로 className에 병합한다.
+
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
+## SlotRecipe 사용 패턴
+
+복합 컴포넌트(슬롯이 여러 개인 경우)는 `createSlotRecipeContext`를 사용한다.
+
+### import 경로
+
+`createSlotRecipeContext`는 반드시 `../../utils/createSlotRecipeContext` 상대 경로로 import한다. `@seed-design/react-utils` 같은 패키지는 존재하지 않는다.
+
+### createSlotRecipeContext 호출 방법
+
+`createSlotRecipeContext`에는 slotRecipe 함수를 직접 전달한다. 객체로 감싸면 타입 불일치가 발생한다.
+
+### withContext 슬롯 연결
+
+각 슬롯 컴포넌트는 `withContext`의 두 번째 인자로 해당 슬롯 이름(예: `"fallback"`)을 지정하여 자동으로 슬롯 className이 적용되게 한다.
+
+### 절대 금지: React 레이어에 style prop 직접 작성
+
+스타일은 반드시 qvism-preset recipe를 통해 className으로 적용해야 한다. style prop을 직접 사용하면 테마, 다크모드, CSS 변수 활용이 불가능하고 스타일 관리가 분산된다. 해당 슬롯의 스타일은 qvism-preset recipe의 `base.slotName`에 작성하고, `withContext`로 연결한다.
diff --git a/skills/create-component/SKILL.md b/skills/create-component/SKILL.md
@@ -9,8 +9,9 @@ description: End-to-end SEED component implementation guide from rootage spec to
 
 ## 실행 절차
 
-1. 대상 범위와 목표 결과를 먼저 확정한다.
-2. `references/`에서 현재 작업에 필요한 문서만 읽는다.
+1. 각 단계에서 수정 대상 폴더의 `AGENTS.md`를 먼저 읽고 해당 패키지의 컨벤션을 확인한다.
+2. 대상 범위와 목표 결과를 먼저 확정한다.
+3. `references/`에서 현재 작업에 필요한 문서만 읽는다.
 3. 문서 절차에 맞춰 구현/수정하고 관련 생성 명령을 실행한다.
 4. 검증 명령을 실행한 뒤 변경 파일과 리스크를 보고한다.
 
diff --git a/skills/create-component/references/implementation-steps.md b/skills/create-component/references/implementation-steps.md
@@ -5,133 +5,70 @@
 **위치**: `packages/react-headless/[name]/`
 **조건**: 데이터 로직이 필요한 경우만 (단순 UI 컴포넌트는 생략)
 
-```typescript
-// use{Component}.ts
-export function useActionButton(props: UseActionButtonProps) {
-  const [pressed, setPressed] = useState(false)
-
-  return {
-    rootProps: {
-      'data-pressed': pressed,
-      'data-disabled': props.disabled,
-      onPointerDown: handlePointerDown,
-      onClick: props.onClick,
-    },
-  }
-}
-```
+Headless 훅은 `use{Component}.ts` 파일에 `use{Component}` 형태로 작성한다. 훅은 `data-pressed`, `data-disabled` 같은 data 속성과 이벤트 핸들러(`onPointerDown`, `onClick` 등)를 `rootProps` 객체로 반환한다.
 
 ## Step 2: Definition (Rootage)
 
 **위치**: `packages/rootage/components/[name].yaml`
 **명령어**: 완료 후 `bun generate:all`
 
-```yaml
-# [component-name].yaml
-id: action-button
-name: Action Button
-description: 사용자 액션을 트리거하는 버튼
-
-slots:
-  root:
-    description: 버튼 루트 요소
-
-variants:
-  tone:
-    values: [neutral, brand, danger]
-    default: neutral
-  size:
-    values: [small, medium, large]
-    default: medium
-
-states:
-  - default
-  - hover
-  - pressed
-  - disabled
-```
+`packages/rootage/components/schema.json`을 참고하여 YAML 파일을 작성한다. 스키마에 정의된 `kind`, `metadata`, `data` 구조를 따르며, slots/variants/definitions를 올바르게 구성한다.
 
 ## Step 3: Recipe (Qvism Preset)
 
 **위치**: `packages/qvism-preset/src/recipes/[name].ts`
 **추가 작업**: `recipes/index.ts`에 export 추가
+**컨벤션**: 구현 전 `packages/qvism-preset/AGENTS.md`를 읽고 해당 패키지의 컨벤션을 확인한다.
 
-```typescript
-import { defineRecipe } from "@seed-design/qvism"
-import { actionButton } from "../vars/component/action-button"
-
-export const actionButtonRecipe = defineRecipe({
-  base: actionButton.root,
-  variants: {
-    tone: {
-      neutral: { /* ... */ },
-      brand: { /* ... */ },
-    },
-    size: {
-      small: { /* ... */ },
-      medium: { /* ... */ },
-    },
-  },
-  defaultVariants: {
-    tone: "neutral",
-    size: "medium",
-  },
-})
-```
+Recipe 파일에서 `../vars/component/`의 생성된 토큰을 import하고, `defineRecipe` 또는 `defineSlotRecipe`로 스타일을 정의한다. 어떤 함수를 사용할지, 슬롯 구조, 전환 시 주의사항은 `packages/qvism-preset/AGENTS.md`에 명시되어 있다.
 
 **주의**: hover 대신 active 상태 사용 (모바일 우선)
 
 ## Step 4: React 컴포넌트
 
 **위치**: `packages/react/src/components/[ComponentName]/`
 **빌드**: 완료 후 `bun packages:build`
+**컨벤션**: 구현 전 `packages/react/AGENTS.md`를 읽고 해당 패키지의 컨벤션을 확인한다.
 
-### 아키텍처 패턴
-
-| 유형 | 패턴 | 예시 |
-|------|------|------|
-| 단일 컴포넌트 | `createRecipeContext` | Button, Badge |
-| 복합 컴포넌트 | `createSlotRecipeContext` | TextField, Chip |
-
-```typescript
-import { ActionButton as HeadlessActionButton } from '@seed-design/react-headless'
-import { actionButton } from '@seed-design/css/components/action-button'
-
-export const ActionButton = forwardRef<HTMLButtonElement, ActionButtonProps>(
-  ({ tone = 'neutral', size = 'medium', ...props }, ref) => {
-    return (
-      <HeadlessActionButton
-        ref={ref}
-        className={actionButton({ tone, size })}
-        {...props}
-      />
-    )
-  }
-)
-ActionButton.displayName = "ActionButton"
-```
-
-## Step 5: Registry UI (선택)
+Variant Props 처리 패턴, 단일/복합 슬롯 패턴, 금지 패턴 등의 상세는 `packages/react/AGENTS.md`에 명시되어 있다.
+
+## Step 5: Registry UI (Snippet 레이어)
 
 **위치**: `docs/registry/ui/[name].tsx`
-**조건**: 복합 컴포넌트의 경우
+
+### Snippet 레이어가 필요한 경우
+
+다음 조건 중 하나라도 해당하면 snippet 레이어를 추가해야 합니다:
+1. **복합 컴포넌트**: Root+Content+Fallback 등 여러 서브컴포넌트를 조합해야 하는 경우 (Avatar, ImageFrame 등)
+2. **서드파티 의존성 통합**: 외부 아이콘 라이브러리나 다른 패키지를 함께 사용해야 하는 경우
+3. **보일러플레이트 단순화**: 사용자가 매번 직접 조합하면 너무 복잡한 경우 (Image.Root + Image.Fallback + Image.Content 등)
+
+### 반대로 Snippet이 필요 없는 경우
+
+- 단일 컴포넌트 (`<Button>`, `<Badge>` 등): `@seed-design/react`에서 직접 사용
+- 이미 심플한 API를 가진 경우
+
+### Snippet 파일 작성 패턴
+
+Snippet 파일은 `"use client"` 선언으로 시작하며, `@seed-design/react`에서 compound 컴포넌트를 import하여 단순화된 API로 래핑한다. Props 인터페이스는 `SeedComponentName.RootProps`를 extends하고, `src`, `alt`, `fallback` 같은 편의 prop을 추가한다. 반드시 `React.forwardRef`로 감싸고 `displayName`을 설정한다. 하위 컴포넌트가 있으면 별도 인터페이스와 함께 re-export한다.
 
 **추가 작업**:
-1. `docs/registry/registry-ui.ts`에 entry 추가
+1. `docs/registry/registry-ui.ts`에 entry 추가 (의존성 버전은 해당 컴포넌트가 추가된 버전 기준)
 2. `bun --filter @seed-design/docs generate:registry` 실행
 
-## Step 6: Examples
+### React 문서 업데이트
 
-**위치**: `docs/components/example/[name]-*.tsx`
+Snippet 레이어가 있는 컴포넌트의 문서는 반드시 다음 형태로 업데이트해야 합니다:
+- `## Installation` 섹션 추가: `npx @seed-design/cli@latest add ui:[name]` 명령어
+- `<ManualInstallation name="[name]" />` 컴포넌트 추가
+- `## Usage`의 import 경로를 `seed-design/ui/[name]`으로 변경
+- Props 섹션 경로를 `./registry/ui/[name].tsx`로 변경
+
+## Step 6: Examples
 
-```typescript
-// action-button-preview.tsx
-import { ActionButton } from "@seed-design/react"
+**위치**: `docs/examples/react/[name]/`
 
-export default function ActionButtonPreview() {
-  return <ActionButton>Click me</ActionButton>
-}
-```
+Snippet 레이어가 있는 경우 `seed-design/ui/[name]`에서 import하고, Layout 컴포넌트(Flex, VStack 등)는 `@seed-design/react`에서 import한다. Snippet 레이어가 없는 경우 `@seed-design/react`에서 직접 import한다.
 
 ## Step 7: Storybook
 
diff --git a/skills/create-component/references/verification-checklist.md b/skills/create-component/references/verification-checklist.md
@@ -17,30 +17,23 @@
 
 ### 잘못된 순서
 
-```text
-❌ React 먼저 → Rootage 나중에
-   → CSS 변수가 없어서 스타일 깨짐
-
-✅ Rootage → generate → Recipe → React → Docs → Test
-```
+반드시 Rootage → generate → Recipe → React → Docs → Test 순서를 따른다. React를 먼저 작성하면 CSS 변수가 없어서 스타일이 깨진다.
 
 ### Recipe export 누락
 
-```text
-❌ Recipe 작성 후 index.ts에 추가 안 함
-   → 컴포넌트에서 import 실패
-
-✅ recipes/index.ts에 반드시 export 추가
-```
+Recipe 작성 후 반드시 `recipes/index.ts`에 export를 추가해야 한다. 누락하면 컴포넌트에서 import가 실패한다.
 
 ### 테스트 생략
 
-```text
-❌ 구현만 하고 Visual Test 안 함
-   → 다크모드/폰트 스케일링 버그 발견 못함
+구현 후 반드시 Agent Browser로 Visual Test를 수행한다. 생략하면 다크모드나 폰트 스케일링 관련 버그를 발견하지 못한다.
+
+### Recipe-React 불일치
+
+Recipe 타입을 변경하거나 슬롯을 추가한 후에는 반드시 `bun generate:all`을 먼저 실행한 뒤 React 코드를 수정한다. 상세는 `packages/qvism-preset/AGENTS.md`와 `packages/css/AGENTS.md` 참조.
+
+### React 컴포넌트 패턴 위반
 
-✅ Agent Browser로 모든 환경 테스트
-```
+variant props 수동 destructuring, 잘못된 import 경로, style prop 직접 사용 등의 금지 패턴은 `packages/react/AGENTS.md`에 명시되어 있다. 구현 전 반드시 확인한다.
 
 ## 생성 파일 (수정 금지)
 
PATCH

echo "Gold patch applied."

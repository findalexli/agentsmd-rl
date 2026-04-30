#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vibe

# Idempotency guard
if grep -qF "When styling base components from other components, always use their `className`" ".cursor/rules/base-components.mdc" && grep -qF "5. **No Static Properties**: Never use the `withStaticProps` utility or assign s" ".cursor/rules/component-internal-structure.mdc" && grep -qF "- **Simpler Components**: For simpler components, not all subdirectories (`hooks" ".cursor/rules/file-structures.mdc" && grep -qF "This rule provides comprehensive guidelines for using [Box](mdc:packages/core/sr" ".cursor/rules/layout-components.mdc" && grep -qF "- **Consistent Typing**: Always check existing similar components to see what Vi" ".cursor/rules/naming-conventions.mdc" && grep -qF "6. **Missing `[data-vibe]` Attribute**: Forgetting to add the mandatory `[data-v" ".cursor/rules/new-component-implementation.mdc" && grep -qF "render: () => <Button kind={Button.kinds.PRIMARY} size={Button.sizes.SMALL}>Clic" ".cursor/rules/storybook-stories.mdc" && grep -qF "description: \"Provides comprehensive guidelines for writing CSS Modules specific" ".cursor/rules/styling-conventions.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/base-components.mdc b/.cursor/rules/base-components.mdc
@@ -240,7 +240,19 @@ Components use CSS custom properties for theming:
 
 ## Common Patterns and Best Practices
 
-### 1. Always Provide Labels
+### 1. Use className Prop for Styling Base Components
+
+When styling base components from other components, always use their `className` prop instead of targeting them with CSS selectors like `[data-vibe]` or `[data-testid]`, element selectors, or other attribute selectors. This maintains clear component boundaries and prevents styling conflicts.
+
+```typescript
+// ✅ Good - Use className prop
+<BaseInput className={styles.myCustomInput} />
+
+// ❌ Bad - Don't target with element or attribute selectors
+// In CSS: button { ... } or [data-testid] { ... }
+```
+
+### 2. Always Provide Labels
 
 ```typescript
 // ✅ Good
diff --git a/.cursor/rules/component-internal-structure.mdc b/.cursor/rules/component-internal-structure.mdc
@@ -13,6 +13,7 @@ alwaysApply: false
 2. **TypeScript**: All components must be written in TypeScript.
 3. **`forwardRef`**: Prefer using `React.forwardRef` for all components that might need to expose their underlying DOM element or instance to parent components. The `ref` should be typed directly on the function's second argument.
 4. **Props Typing and Destructuring**: Props must be destructured in the component function's first argument, and this argument must be explicitly typed with the component's props type.
+5. **No Static Properties**: Never use the `withStaticProps` utility or assign static properties to components. Components should remain without attached static properties. This means avoiding patterns like `MyComponent.colors = {...}`, `MyComponent.sizes = {...}`, and even avoiding `MyComponent.displayName = "..."`.
 
 ## File Structure (within the `.tsx` file)
 
@@ -52,6 +53,31 @@ const MyComponent = React.forwardRef(
 );
 ```
 
+#### Dismissible Component Props Pattern
+
+**If your component can be dismissed/closed**, follow this established pattern to avoid redundant props:
+
+- **Use `onClose` prop as both handler and boolean indicator** - don't add separate `dismissible` or `closable` props
+- **Conditional rendering based on `onClose` presence**: `{onClose && <CloseButton onClick={onClose} />}`
+
+**Implementation Example**:
+
+```typescript
+const MyComponent = ({ onClose, closeButtonAriaLabel = "Close", ...otherProps }: MyComponentProps) => {
+  return (
+    <div>
+      {/* ...Component content */}
+      {onClose && <IconButton ariaLabel={closeButtonAriaLabel} icon={CloseIcon} onClick={onClose} />}
+    </div>
+  );
+};
+```
+
+**Why This Pattern**:
+
+- **Simplifies API**: No need for separate boolean props like `dismissible={true}`
+- **Clear Intent**: If user wants dismissible behavior, they pass `onClose`
+
 ### 3. State and Hooks
 
 - **`useState`**: Use `useState` for simple local state.
diff --git a/.cursor/rules/file-structures.mdc b/.cursor/rules/file-structures.mdc
@@ -34,16 +34,32 @@ Each component within `packages/core/src/components/` should follow a consistent
 
 ### Subdirectories
 
-- **`__tests__/`**: Contains unit and integration tests for the component.
+- **`__tests__/`**: Contains unit and integration tests **only for the main component files** in the root directory.
   - Files within this directory follow the pattern `ComponentName.test.ts`.
+  - **DO NOT** place tests for subcomponents, hooks, utils, or context in this directory.
 - **`__stories__/`**: Holds Storybook stories for the component.
   - Files are typically named `ComponentName.stories.tsx`.
 - **`components/`**: For more complex components, this directory can house sub-components that are only used by `ComponentName`.
+  - **Each subcomponent should have its own `__tests__/` directory** if tests are needed.
+  - Structure: `ComponentName/components/SubComponent/__tests__/SubComponent.test.tsx`
 - **`hooks/`**: Custom React hooks that are specific to `ComponentName` and not intended for reuse elsewhere.
+  - **Should contain a `__tests__/` subdirectory** if hook tests are needed.
+  - Structure: `ComponentName/hooks/__tests__/useHookName.test.ts`
+- **`utils/`**: Utility functions specific to `ComponentName`.
+  - **Should contain a `__tests__/` subdirectory** if utility tests are needed.
+  - Structure: `ComponentName/utils/__tests__/utilityName.test.ts`
 - **`context/`**: If a component uses React Context, the context definition, provider, and consumer hook should be placed in this subdirectory (e.g., `ComponentName/context/ComponentNameContext.ts`).
+  - **Should contain a `__tests__/` subdirectory** if context tests are needed.
+  - Structure: `ComponentName/context/__tests__/ComponentNameContext.test.ts`
+- **`consts/`**: Component-specific constant values that are not intended for reuse elsewhere.
+  - **DO NOT** place constants files at the root of the component directory.
+  - **Use meaningful file names** that describe the purpose, not generic names like `MyComponentConstants.ts` or `consts.ts`.
+  - Examples: `ComponentName/consts/variants.ts`, `ComponentName/consts/validate-colors.ts`, `ComponentName/consts/sizes.ts`
+  - **Should contain a `__tests__/` subdirectory** if constants tests are needed.
+  - Structure: `ComponentName/consts/__tests__/sizes.test.ts`
 
 ### General Guidelines
 
-- **Simpler Components**: For simpler components, not all subdirectories (`hooks/`, `utils/`, `components/`, `context/`) are necessary. Files like `ComponentName.tsx`, `ComponentName.types.ts`, `ComponentName.module.scss`, `index.ts`, and directories for tests (`__tests__/`) and stories (`__stories__/`) are sufficient in most of the cases.
-- **Reusability**: If a hook or utility is reusable across multiple components (not potentially reusable, but actually reused in more than one component), it should be placed in the top-level `packages/core/src/hooks/` or `packages/core/src/utils/` directories, respectively.
+- **Simpler Components**: For simpler components, not all subdirectories (`hooks/`, `utils/`, `components/`, `context/`, `consts/`) are necessary. Files like `ComponentName.tsx`, `ComponentName.types.ts`, `ComponentName.module.scss`, `index.ts`, and directories for tests (`__tests__/`) and stories (`__stories__/`) are sufficient in most of the cases.
+- **Reusability**: If a hook, utility, or constant is reusable across multiple components (not potentially reusable, but actually reused in more than one component), it should be placed in the top-level `packages/core/src/hooks/`, `packages/core/src/utils/`, or `packages/core/src/constants/` directories, respectively.
 - **Exports**: The `index.ts` file in each component directory should be the primary point of export for that component and its related parts. The main `packages/core/src/index.ts` should then re-export these components.
diff --git a/.cursor/rules/layout-components.mdc b/.cursor/rules/layout-components.mdc
@@ -0,0 +1,327 @@
+---
+description: Guidelines for using Box and Flex layout components in the @vibe/core library instead of custom CSS for spacing, borders, and flexbox layouts.
+globs: *.tsx,*.ts
+---
+
+# Layout Components Guidelines
+
+This rule provides comprehensive guidelines for using [Box](mdc:packages/core/src/components/Box/Box.tsx) and [Flex](mdc:packages/core/src/components/Flex/Flex.tsx) components from `@vibe/core` instead of custom CSS for layout, spacing, borders, and containers.
+
+## Core Principle: Props Over CSS
+
+**Always prefer component props over custom CSS** for layout properties that Box and Flex provide. This ensures:
+
+- Consistent design token usage
+- Better maintainability
+- Type safety
+- Reduced CSS bundle size
+- Design system compliance
+
+## Box Component Usage
+
+### When to Use Box
+
+- **Container styling**: Backgrounds, borders, shadows, padding, margins
+- **Scrollable containers**: Use `scrollable` prop instead of `overflow: auto` in CSS
+- **Bordered containers**: Use `border` props instead of CSS border
+- **Spacing containers**: Use margin/padding props instead of CSS spacing
+- **Styled wrappers**: Any div that needs visual styling
+
+### Box Props Reference
+
+#### Spacing Props
+
+```tsx
+// ❌ Avoid CSS
+<div className={styles.container}>
+  <Content />
+</div>
+// .container { padding: var(--space-16); margin-bottom: var(--space-24); }
+
+// ✅ Prefer Box props
+<Box padding="medium" marginBottom="large">
+  <Content />
+</Box>
+```
+
+**Available spacing values**: `xs`, `small`, `medium`, `large`, `xl`, `xxl`, `xxxl`.
+
+If needing for a size that does not exist on `Box` (like `var(--space-12)`), you can use css for this value instead of using a prop.
+
+- Margin props also support: `auto`, `none`
+- Directional props: `marginX`, `marginY`, `marginTop`, `marginEnd`, `marginBottom`, `marginStart`
+- Directional props: `paddingX`, `paddingY`, `paddingTop`, `paddingEnd`, `paddingBottom`, `paddingStart`
+
+#### Border & Visual Props
+
+```tsx
+// ❌ Avoid CSS
+<div className={styles.bordered}>
+  <Content />
+</div>
+// .bordered { border: 1px solid var(--border-color); border-radius: 8px; }
+
+// ✅ Prefer Box props
+<Box border borderColor="uiBorderColor" rounded="medium">
+  <Content />
+</Box>
+```
+
+**Border colors**: `uiBorderColor`, `layoutBorderColor`
+**Rounded values**: `small`, `medium`, `big`
+**Shadow values**: `xs`, `small`, `medium`, `large`
+
+#### Scrollable Containers
+
+```tsx
+// ❌ Avoid CSS
+<div className={styles.scrollableContainer}>
+  <Content />
+</div>
+// .scrollableContainer { overflow: auto; }
+
+// ✅ Prefer Box scrollable prop
+<Box scrollable>
+  <Content />
+</Box>
+```
+
+#### Background & Text Colors
+
+```tsx
+// ❌ Avoid CSS
+<div className={styles.cardContainer}>
+  <Content />
+</div>
+// .cardContainer { background-color: var(--secondary-background-color); }
+
+// ✅ Prefer Box props
+<Box backgroundColor="secondaryBackgroundColor" textColor="primaryTextColor">
+  <Content />
+</Box>
+```
+
+**Background colors**: `primaryBackgroundColor`, `secondaryBackgroundColor`, `greyBackgroundColor`, `allgreyBackgroundColor`, `invertedColorBackground`
+**Text colors**: `primaryTextColor`, `textColorOnInverted`, `secondaryTextColor`
+
+## Flex Component Usage
+
+### When to Use Flex
+
+- **Layout positioning**: Arrange elements horizontally or vertically
+- **Gap spacing**: Space between flex items
+- **Alignment**: Justify and align flex items
+- **Responsive layouts**: Wrapping flex containers
+- **Toolbar/header layouts**: Horizontal arrangements with spacing
+
+### Flex Props Reference
+
+#### Basic Layout
+
+```tsx
+// ❌ Avoid CSS
+<div className={styles.flexContainer}>
+  <Item1 />
+  <Item2 />
+  <Item3 />
+</div>
+// .flexContainer { display: flex; gap: 16px; justify-content: space-between; }
+
+// ✅ Prefer Flex props
+<Flex gap="medium" justify="space-between">
+  <Item1 />
+  <Item2 />
+  <Item3 />
+</Flex>
+```
+
+**Direction values**: `row` (default), `column`
+**Gap values**: `xs` (4px), `small` (8px), `medium` (16px), `large` (24px), or custom number in px
+**Justify values**: `start`, `center`, `end`, `stretch`, `space-around`, `space-between`, `initial`
+**Align values**: `start`, `center`, `end`, `stretch`, `baseline`, `initial`
+
+#### Common Patterns
+
+```tsx
+// Horizontal toolbar
+<Flex gap="small" justify="space-between" align="center">
+  <Button>Action 1</Button>
+  <Button>Action 2</Button>
+</Flex>
+
+// Vertical stack
+<Flex direction="column" gap="medium">
+  <Item1 />
+  <Item2 />
+  <Item3 />
+</Flex>
+
+// Centered content
+<Flex justify="center" align="center">
+  <Content />
+</Flex>
+
+// With custom gap (px value)
+<Flex gap={32} direction="column">
+  <Item1 />
+  <Item2 />
+</Flex>
+```
+
+#### Clickable Flex
+
+When providing `onClick`, Flex automatically wraps with Clickable component:
+
+```tsx
+<Flex gap="small" onClick={handleClick} ariaLabel="Clickable toolbar" tabIndex={0}>
+  <Item1 />
+  <Item2 />
+</Flex>
+```
+
+## Component Combination Patterns
+
+### Box + Flex for Complex Layouts
+
+```tsx
+// Container with border and internal flex layout
+<Box border rounded="medium" padding="medium">
+  <Flex gap="small" justify="space-between" align="center">
+    <Text>Title</Text>
+    <Button>Action</Button>
+  </Flex>
+</Box>
+
+// Scrollable flex container
+<Box scrollable>
+  <Flex direction="column" gap="small">
+    {items.map(item => <Item key={item.id} {...item} />)}
+  </Flex>
+</Box>
+```
+
+### Nested Layout Structure
+
+```tsx
+// Page layout example
+<Box padding="large">
+  <Flex direction="column" gap="large">
+    {/* Header */}
+    <Flex justify="space-between" align="center">
+      <Heading>Page Title</Heading>
+      <Button>Action</Button>
+    </Flex>
+
+    {/* Content cards */}
+    <Flex gap="medium" wrap>
+      {cards.map(card => (
+        <Box key={card.id} border rounded="medium" padding="medium" backgroundColor="secondaryBackgroundColor">
+          <Card {...card} />
+        </Box>
+      ))}
+    </Flex>
+  </Flex>
+</Box>
+```
+
+## Migration Guidelines
+
+### From CSS to Box
+
+1. **Replace border CSS**: `border: 1px solid var(--border-color)` → `border` prop
+2. **Replace padding/margin CSS**: `padding: var(--spacing-medium)` → `padding="medium"`
+3. **Replace overflow CSS**: `overflow: auto` → `scrollable` prop
+4. **Replace background CSS**: `background-color: var(--secondary-bg)` → `backgroundColor="secondaryBackgroundColor"`
+
+### From CSS to Flex
+
+1. **Replace display flex**: `display: flex` → `<Flex>`
+2. **Replace gap CSS**: `gap: 16px` → `gap="medium"` or `gap={16}`
+3. **Replace justify-content**: `justify-content: space-between` → `justify="space-between"`
+4. **Replace align-items**: `align-items: center` → `align="center"`
+5. **Replace flex-direction**: `flex-direction: column` → `direction="column"`
+
+## Anti-Patterns to Avoid
+
+### ❌ Don't Use CSS When Props Are Available
+
+```tsx
+// ❌ Bad
+<div className={styles.container}>
+  <Content />
+</div>
+// .container {
+//   display: flex;
+//   gap: 16px;
+//   padding: 24px;
+//   border: 1px solid var(--border-color);
+// }
+
+// ✅ Good
+<Box border padding="large">
+  <Flex gap="medium">
+    <Content />
+  </Flex>
+</Box>
+```
+
+### ❌ Don't Mix CSS Layout with Component Props
+
+```tsx
+// ❌ Bad - mixing CSS flex with Flex props
+<Flex className={styles.customFlex} gap="medium">
+  <Content />
+</Flex>
+// .customFlex { justify-content: space-between; } // Use justify prop instead
+
+// ✅ Good
+<Flex gap="medium" justify="space-between">
+  <Content />
+</Flex>
+```
+
+### ❌ Don't Use Plain Divs for Styled Containers
+
+```tsx
+// ❌ Bad
+<div className={styles.card}>
+  <div className={styles.scrollableContent}>
+    <Content />
+  </div>
+</div>
+
+// ✅ Good
+<Box border rounded="medium" padding="medium">
+  <Box scrollable>
+    <Content />
+  </Box>
+</Box>
+```
+
+## Element Types
+
+Both Box and Flex support `elementType` prop to render as different HTML elements:
+
+```tsx
+<Box elementType="section" padding="large">
+  <Content />
+</Box>
+
+<Flex elementType="header" justify="space-between">
+  <Logo />
+  <Navigation />
+</Flex>
+```
+
+## Accessibility
+
+- Use `ariaLabel` and `ariaLabelledby` props on Flex when it's a meaningful container
+- Box and Flex support all standard HTML accessibility attributes
+- When using `onClick` on Flex, proper accessibility attributes are automatically handled
+
+## Examples from Codebase
+
+See usage examples in:
+
+- [Box Stories](mdc:packages/core/src/components/Box/__stories__/Box.stories.tsx)
+- [Flex Stories](mdc:packages/core/src/components/Flex/__stories__/Flex.stories.tsx)
diff --git a/.cursor/rules/naming-conventions.mdc b/.cursor/rules/naming-conventions.mdc
@@ -37,14 +37,19 @@ This document outlines the naming conventions to be followed when developing wit
 
 ### Sub-directories (within a component folder)
 
-- **Tests**: Test files SHOULD be placed in a `__tests__` subdirectory.
-  - Test files themselves typically follow the pattern `ComponentName.test.tsx`.
+- **Tests**: Test files SHOULD be co-located with the code they test in respective `__tests__` subdirectories.
+  - **Main Component Tests**: Place in `ComponentName/__tests__/ComponentName.test.tsx`
+  - **Subcomponent Tests**: Place in `ComponentName/components/SubComponent/__tests__/SubComponent.test.tsx`
+  - **Hook Tests**: Place in `ComponentName/hooks/__tests__/useHookName.test.ts`
+  - **Utility Tests**: Place in `ComponentName/utils/__tests__/utilityName.test.ts`
+  - **Context Tests**: Place in `ComponentName/context/__tests__/ComponentNameContext.test.ts`
+  - **DO NOT** centralize all tests in the component root `__tests__` directory.
 - **Stories**: Storybook files SHOULD be placed in a `__stories__` subdirectory.
   - Story files typically follow the pattern `ComponentName.stories.tsx`.
   - Refer to the storybook-stories.mdc file in the monorepo for Storybook specific conventions.
 - **Helper/Utility Files**: Utility functions or helper components specific to a single component can be placed in a `helper` or `utils` subdirectory, or directly within the component folder if small and highly specific.
   - File names SHOULD be `camelCase.ts` for utils/helpers or `PascalCase.ts` if they export React components.
-- **Custom Hooks**: Component-specific custom hooks SHOULD be placed in a `__hooks__` subdirectory.
+- **Custom Hooks**: Component-specific custom hooks SHOULD be placed in a `hooks` subdirectory.
   - Hook files SHOULD follow the pattern `useHookName.ts` and use camelCase.
   - If there's only one hook that's tightly coupled to the component, it can be placed directly in the component folder as `useHookName.ts`.
 
@@ -69,6 +74,11 @@ This document outlines the naming conventions to be followed when developing wit
     - Common, unambiguous adjective props like `loading`, `active`, `open`, `checked`, or `required` are also acceptable.
     - However, if the HTML attribute is `disabled`, using `disabled` is acceptable for consistency.
 
+#### Prop Values
+
+- **String Literals**: Component prop values should use string literals rather than static properties
+  - Example: `<Button size="small" />` instead of `<Button size={Button.sizes.SMALL} />`
+
 ### Variable and Function Names
 
 - Local variables and function names SHOULD use `camelCase`.
@@ -88,6 +98,15 @@ This document outlines the naming conventions to be followed when developing wit
   - Example: `type UserProfile = { /* ... */ };`.
   - Example: `interface ComponentProps { /* ... */ }`.
 
+### Vibe Standard Types
+
+When working with Vibe components, always use the established standard types for common prop patterns:
+
+- **Icon Props**: Always use `SubIcon` type for any prop that accept icons.
+  - Example: `icon?: SubIcon;` instead of generic types like `ReactNode` or custom icon types.
+- **Component Props**: Extend `VibeComponentProps` for component props (to get `className`, `id`, `data-testid`).
+- **Consistent Typing**: Always check existing similar components to see what Vibe standard types they use before creating custom types.
+
 ### CSS Class Names
 
 - CSS class names within `.module.scss` files MUST use `camelCase`.
diff --git a/.cursor/rules/new-component-implementation.mdc b/.cursor/rules/new-component-implementation.mdc
@@ -57,6 +57,34 @@ Research the exact APIs of Vibe components you'll integrate with:
 - Import from established Vibe components
 - Follow existing test ID patterns from [constants.ts](mdc:packages/core/src/tests/constants.ts)
 - Use CSS Modules for styling
+- **MANDATORY**: Add `[data-vibe]` attribute for component identification
+
+#### Essential `[data-vibe]` Attribute Implementation
+
+**CRITICAL**: Every new component MUST include the `[data-vibe]` attribute on its root element for component identification in the DOM.
+
+**Import Pattern**:
+
+```tsx
+import { ComponentVibeId } from "../../tests/constants";
+```
+
+**Usage Pattern**:
+Add to the root element's props:
+
+```tsx
+data-vibe={ComponentVibeId.ATTENTION_BOX}
+```
+
+**Implementation Examples**:
+
+**Enum Naming Pattern**:
+The `ComponentVibeId` enum follows SCREAMING_SNAKE_CASE format. For example:
+
+- `Button` → `ComponentVibeId.BUTTON`
+- `AttentionBox` → `ComponentVibeId.ATTENTION_BOX`
+- `MenuButton` → `ComponentVibeId.MENU_BUTTON`
+- `LinearProgressBar` → `ComponentVibeId.LINEAR_PROGRESS_BAR`
 
 **References**:
 
@@ -65,33 +93,60 @@ Research the exact APIs of Vibe components you'll integrate with:
 - [react-context](mdc:.cursor/rules/react-context.mdc) if your component needs to use or provide React Context
 - [naming-conventions](mdc:.cursor/rules/naming-conventions.mdc) for component and prop naming patterns
 
-### 3. Styles (`ComponentName.module.scss`)
+### 3. Component Constants (Optional: `consts/` directory)
+
+**If your component needs constant values**, organize them properly:
+
+- **MANDATORY**: Place constants files inside a `consts/` folder, never at the component root
+- **MANDATORY**: Use meaningful file names that describe purpose, not generic names like `MyComponentConstants.ts` or `consts.ts`
+- **Examples of good names**: `variants.ts`, `validate-colors.ts`, `events.ts`, `sizes.ts`
+
+**Reusability Rule**: If constants are used across multiple components, place them in the top-level `packages/core/src/constants/` directory instead.
+
+**Reference**: [file-structures](mdc:.cursor/rules/file-structures.mdc) for detailed constants organization patterns.
+
+### 4. Styles (`ComponentName.module.scss`)
 
 - NEVER Import anything inside the module scss file
 - Use established design tokens and spacing variables
 
 **Reference**: [styling-conventions](mdc:.cursor/rules/styling-conventions.mdc) for comprehensive CSS Modules guidelines, design token usage, and styling best practices.
 
-### 4. Index Exports (`index.ts`)
+### 5. Index Exports (`index.ts`)
 
 - On the same root directory of the component (e.g., `packages/core/src/components/MyComponent/index.ts`)
 - Export both component and types
 - Follow pattern: `export { default as ComponentName } from "./ComponentName"`
 
 **Reference**: [file-structures](mdc:.cursor/rules/file-structures.mdc) for export patterns and file organization conventions.
 
-### 5. Add to Global Exports
+### 6. Add to Global Exports
 
 - Update [components/index.ts](mdc:packages/core/src/components/index.ts) in alphabetical order
 - Add test IDs to [constants.ts](mdc:packages/core/src/tests/constants.ts) enum
-- Add to `ComponentVibeId` enum if needed
+- **MANDATORY**: Add your component to the `ComponentVibeId` enum in [constants.ts](mdc:packages/core/src/tests/constants.ts)
+
+#### Adding ComponentVibeId Enum Value
+
+**CRITICAL**: Every new component MUST have a corresponding entry in the `ComponentVibeId` enum.
+
+**Steps**:
+
+1. Find the `ComponentVibeId` enum
+2. Add your component in alphabetical order using SCREAMING_SNAKE_CASE format
+
+**Naming Convention**: Use the exact component name as the enum value, but the key should be in SCREAMING_SNAKE_CASE:
+
+- `Button` → `BUTTON = "Button"`
+- `MenuButton` → `MENU_BUTTON = "MenuButton"`  
+- `LinearProgressBar` → `LINEAR_PROGRESS_BAR = "LinearProgressBar"`
 
 **References**:
 
 - [file-structures](mdc:.cursor/rules/file-structures.mdc) for global export patterns
 - [monorepo-structure](mdc:.cursor/rules/monorepo-structure.mdc) for understanding where and how to add global exports
 
-### 6. Tests (`__tests__/ComponentName.test.tsx`)
+### 7. Tests (`__tests__/ComponentName.test.tsx`)
 
 - Follow testing patterns from similar components
 - Test actual component behavior, not assumptions
@@ -101,8 +156,9 @@ Research the exact APIs of Vibe components you'll integrate with:
 **Reference**:
 
 - [accessibility-guidelines](mdc:.cursor/rules/accessibility-guidelines.mdc) for comprehensive accessibility testing requirements and patterns.
+- [file-structures](mdc:.cursor/rules/file-structures.mdc) for detailed test organization patterns.
 
-### 7. Stories (`__stories__/ComponentName.stories.tsx`)
+### 8. Stories (`__stories__/ComponentName.stories.tsx`)
 
 - Create comprehensive examples covering all variants
 
@@ -113,7 +169,7 @@ Research the exact APIs of Vibe components you'll integrate with:
 ### Development Validation
 
 1. **TypeScript Check**
-2. **Test Suite**: `yarn test src/components/ComponentName/`
+2. **Test Suite**: `yarn test src/components/ComponentName/` (will recursively run all tests in subdirectories)
 3. **Lint and Format**: `yarn prettier --write src/components/ComponentName/` then `yarn lint src/components/ComponentName/ --fix`
 
 ### Integration Verification
@@ -130,6 +186,13 @@ Research the exact APIs of Vibe components you'll integrate with:
 - **Study Patterns**: Look at how similar components handle similar problems
 - **Understand Context**: Review existing test patterns and story structures
 
+### Modern Prop Patterns
+
+- **Use String Literals**: Define prop values as string literals instead of static properties
+  - ✅ Prefer: `<MyComponent size="large" variant="primary" />`
+  - ❌ Avoid: `<MyComponent size={MyComponent.sizes.LARGE} variant={MyComponent.variants.PRIMARY} />`
+- **Backward Compatibility**: While legacy static properties may exist in the codebase, new components should not include them
+
 ### Systematic Progression
 
 - **Follow Order**: Complete each phase before moving to next
@@ -149,5 +212,6 @@ Research the exact APIs of Vibe components you'll integrate with:
 3. **Test Assumptions**: Test actual behavior (disabled buttons may use `aria-disabled` vs `disabled`)
 4. **Missing Integration**: Forgetting to add exports to main index files or test constants
 5. **Design Token Guessing**: Check existing SCSS files for available CSS custom properties
+6. **Missing `[data-vibe]` Attribute**: Forgetting to add the mandatory `[data-vibe]` attribute or missing the corresponding `ComponentVibeId` enum entry
 
 This workflow ensures consistent, high-quality component implementation that integrates seamlessly with the Vibe design system.
diff --git a/.cursor/rules/storybook-stories.mdc b/.cursor/rules/storybook-stories.mdc
@@ -102,6 +102,24 @@ export const ComplexExample: Story = {
   - They can choose to use some of the `args` from the controls (e.g., for base styling or less critical props) or completely ignore/override them with hardcoded values to ensure the story accurately depicts the intended specific state.
 - Keep render functions as simple as possible, focusing on the component being storied.
 
+#### Prop Value Best Practices
+
+When writing stories, always use string literal prop values instead of static properties:
+
+```typescript
+// ✅ Preferred approach
+export const PrimaryButton: Story = {
+  render: () => <Button kind="primary" size="small">Click me</Button>
+};
+
+// ❌ Avoid (legacy pattern) 
+export const PrimaryButton: Story = {
+  render: () => <Button kind={Button.kinds.PRIMARY} size={Button.sizes.SMALL}>Click me</Button>
+};
+```
+
+This approach provides better IntelliSense, type safety, and follows modern Vibe conventions.
+
 Example of an `Overview` story's render function:
 
 ```typescript
diff --git a/.cursor/rules/styling-conventions.mdc b/.cursor/rules/styling-conventions.mdc
@@ -1,5 +1,5 @@
 ---
-description: "Provides comprehensive guidelines for writing CSS Modules specifically for UI components within the `@vibe/core` library (under `packages/core/src/components/`). This rule covers file naming conventions (e.g., `ComponentName.module.scss`), CSS nesting, mandatory browser compatibility, strategies for adopting newer CSS APIs with fallbacks, the exclusive use of design tokens from `monday-ui-style` (via CSS custom properties like `var(--primary-text-color)`), discouraging mixin usage from `monday-ui-style`, typography best practices (using `Text`/`Heading` components instead of direct font tokens), `camelCase` class naming, and common anti-patterns like avoiding theme-specific styles directly in component SCSS. Activate this rule when working with `.module.scss` files in `packages/core/src/components/` or when styling Vibe core components."
+description: "Provides comprehensive guidelines for writing CSS Modules specifically for UI components within the `@vibe/core` library (under `packages/core/src/components/`). This rule covers file naming conventions (e.g., `ComponentName.module.scss`), CSS nesting, mandatory browser compatibility, strategies for adopting newer CSS APIs with fallbacks, the exclusive use of design tokens from `monday-ui-style` (via CSS custom properties like `var(--primary-text-color)`), discouraging mixin usage from `monday-ui-style`, typography best practices (using `Text`/`Heading` components instead of direct font tokens), `camelCase` class naming, and common anti-patterns like avoiding theme-specific styles directly in component SCSS, never using `:global`, and never using `!important`. Activate this rule when working with `.module.scss` files in `packages/core/src/components/` or when styling Vibe core components."
 globs:
   - "packages/core/src/components/**/*.module.scss"
 alwaysApply: false
@@ -35,6 +35,8 @@ This document outlines the rules and best practices for writing styles using SCS
     }
     ```
 
+- **Always Use Logical CSS Properties:** Use logical CSS properties instead of physical properties to ensure proper RTL support and internationalization. Logical properties are direction-agnostic and automatically adapt to different writing modes.
+
 - **Chrome 85+ Compatibility:** All styling **must** be compatible with Chrome version 85 and newer. Avoid using CSS features not supported by this baseline.
 - **Handling Newer CSS APIs:**
 
@@ -85,5 +87,8 @@ This document outlines the rules and best practices for writing styles using SCS
 ## 7. Anti-Patterns and Considerations
 
 - **No Theme-Specific Styles in Component SCSS:** Avoid embedding theme-specific rules (e.g., using `:global(.dark-app-theme) &`) directly within a component's `.module.scss` file. This is considered an anti-pattern as components should be theme-agnostic by default, adapting to themes via design tokens.
+- **Never Use :global:** The use of `:global()` in SCSS Modules is strictly prohibited. SCSS Modules are designed to provide scoped styles, and using `:global()` defeats this purpose and can lead to unintended side effects and style conflicts.
+- **Never Use !important:** The use of `!important` in CSS is strictly prohibited. Instead of using `!important`, resolve specificity issues other way.
+- **ALWAYS Use className Prop for Components:** When styling internal reusable components/base components, always use their `className` prop instead of targeting them in the scss file with other selectors such as `[data-vibe]`, element selectors like `button`, or other attribute selectors. This maintains clear component boundaries and prevents unintended styling conflicts.
 - **Responsiveness:** Do not implement responsive styles (e.g., using media queries, container queries) unless explicitly requested by the user or task.
 - **Focus on Maintainability:** Write styles that are maintainable. Avoid overly specific selectors that might break easily with small markup changes.
PATCH

echo "Gold patch applied."

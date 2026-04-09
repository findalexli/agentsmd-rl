# Task: Simplify Redundant CSS-in-JS Style Selector Keys

## Problem

The Ant Design codebase uses CSS-in-JS (via `@ant-design/cssinjs`) to define component styles. Throughout the codebase, there are style files that use unnecessarily verbose multi-line template literal syntax for CSS selector keys where single-line strings would suffice.

For example, in `components/collapse/style/index.ts`, the current code uses:

```typescript
[`& ${componentCls}-item-disabled > ${componentCls}-header`]: {
  [`
    &,
    & > .arrow
  `]: {
    color: colorTextDisabled,
    cursor: 'not-allowed',
  },
},
```

This could be simplified to:

```typescript
[`& ${componentCls}-item-disabled > ${componentCls}-header`]: {
  '&, & > .arrow': {
    color: colorTextDisabled,
    cursor: 'not-allowed',
  },
},
```

Similar patterns exist in multiple style files:
- `components/date-picker/style/panel.ts`
- `components/dropdown/style/index.ts`
- `components/form/style/index.ts`
- `components/menu/style/index.ts`
- `components/table/style/bordered.ts`
- `components/table/style/empty.ts`
- `components/table/style/index.ts`
- `components/typography/style/index.ts`
- `components/typography/style/mixins.ts`

## Task

Refactor the CSS selector keys in these style files to use simpler single-line string literals instead of multi-line template literals. The refactoring should:

1. Preserve the exact same CSS output (the selectors must remain semantically identical)
2. Only affect static selector keys that don't require template literal interpolation
3. Remove unnecessary whitespace and newlines from selector strings
4. Use single quotes for simple strings, backticks only when interpolation is needed

## Guidelines

- Look for patterns where template literals (`` `...` ``) are used for static selector strings
- Replace multi-line selectors like:
  ```typescript
  [`
    &-hidden,
    &-menu-hidden,
    &-menu-submenu-hidden
  `]
  ```
  With single-line:
  ```typescript
  '&-hidden, &-menu-hidden, &-menu-submenu-hidden'
  ```
- Keep template literals (backticks) only when variable interpolation is actually used
- Ensure TypeScript compiles without errors after the changes

The goal is to improve code readability and consistency without changing any runtime behavior.

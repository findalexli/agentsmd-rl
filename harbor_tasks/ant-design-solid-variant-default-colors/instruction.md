# Task: Add Default Colors for Solid Variants in Button and Tag Components

## Problem Description

When using the `variant="solid"` prop on `Button` or `Tag` components **without explicitly setting a `color` prop**, the components do not render with appropriate default colors. This leads to visually incorrect or unstyled components.

### Expected Behavior

1. **Button**: When `variant="solid"` is used without a `color` prop, the button should default to `color="primary"`.
2. **Tag**: When `variant="solid"` is used without a `color` prop, the tag should default to `color="default"`.

3. **ConfigProvider Support**: The same behavior should apply when these variants are set globally via `ConfigProvider`:
   - `<ConfigProvider button={{ variant: 'solid' }}>` should make all buttons default to `color="primary"`
   - `<ConfigProvider tag={{ variant: 'solid' }}>` should make all tags default to `color="default"`

### Affected Files

- `components/button/Button.tsx` - Main Button component logic
- `components/tag/hooks/useColor.ts` - Tag color handling hook

### What to Look For

In `Button.tsx`, look for the color/variant pair logic. The component calculates a `[color, variant]` tuple based on props and context. The fix should add fallback logic when `variant === 'solid'` but no color is explicitly set.

In `useColor.ts`, look for how the color value is processed. When the color is `undefined` and the variant is `solid`, it should default to `'default'`.

### Testing Your Changes

The existing tests in the repository provide guidance on how to verify your changes:
- `components/button/__tests__/index.test.tsx`
- `components/tag/__tests__/index.test.tsx`

Your implementation should pass these test patterns:
- Button with `variant="solid"` should have classes: `ant-btn-variant-solid` AND `ant-btn-color-primary`
- Tag with `variant="solid"` should have classes: `ant-tag-solid` AND `ant-tag-default`
- Tag with `variant="outlined"` should NOT have `ant-tag-default` class

### Repository Structure

```
components/
├── button/
│   ├── Button.tsx              # Main Button implementation
│   └── __tests__/
│       └── index.test.tsx      # Existing Button tests
└── tag/
    ├── hooks/
    │   └── useColor.ts         # Tag color logic
    └── __tests__/
        └── index.test.tsx      # Existing Tag tests
```

### Notes

- This is a React + TypeScript codebase
- The project uses CSS-in-JS with className patterns like `ant-btn-color-*` and `ant-tag-*`
- Follow the existing code style in the files you modify
- Do NOT modify test files as part of your solution - the tests should pass with your implementation changes only

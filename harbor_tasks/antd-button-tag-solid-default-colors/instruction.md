# Task: Add Default Colors for Solid Variants

## Problem

When using `variant="solid"` on Button or Tag components without explicitly specifying a `color` prop, the components do not receive a default color assignment. This causes styling issues where the solid variant doesn't have proper color styling applied.

## Codebase Context

### Button (`components/button/Button.tsx`)

The Button component is defined as `InternalCompoundedButton` using `React.forwardRef`. It computes a `[color, variant]` pair based on direct props and ConfigProvider context values. The relevant variables in this computation are:

- `variant` / `contextVariant` — the variant from direct props / ConfigProvider context
- `color` / `contextColor` — the color from direct props / ConfigProvider context

The function returns a `[color, variant]` tuple in various cases. When neither a direct color nor a context color is provided, it falls through to a default `['default', 'outlined']`.

### Tag (`components/tag/hooks/useColor.ts`)

The Tag's `useColor` hook resolves color information using:

- `nextVariant` — the resolved variant
- `nextColor` — the resolved color (may be `undefined` when no color prop is given)
- `isPresetColor()` / `isPresetStatusColor()` — utility functions for checking color types

After resolving `nextColor` from the raw `color` prop, the hook checks whether the color is a preset or status color, then determines the final styling.

## Expected Behavior

### Button

When no explicit color is provided and the variant is solid:

1. After the existing merged-type handling and before the context fallback, the code should check `if (variant === 'solid')` and return `['primary', variant]` in that case
2. After the context fallback (where both `contextColor` and `contextVariant` are set), the code should check `if (contextVariant === 'solid')` and return `['primary', contextVariant]`
3. Non-solid variants must keep existing behavior, falling through to `['default', 'outlined']`
4. The component must continue to be defined using `React.forwardRef` and named `InternalCompoundedButton`

### Tag

When no explicit color is provided:

1. The `nextColor` variable needs to be changed from `const` to `let` so it can be reassigned
2. After `nextColor` is computed from the raw `color` prop, a condition checking `nextColor === undefined` combined with `nextVariant === 'solid'` should assign `nextColor = 'default'`
3. The preset and status checks below must call `isPresetColor(nextColor)` and `isPresetStatusColor(nextColor)` — using the resolved `nextColor` variable rather than the raw `color` prop — so they correctly account for the defaulted value
4. Non-solid variants should NOT receive default colors

## Files to Modify

- `components/button/Button.tsx` — add default color logic for Button
- `components/tag/hooks/useColor.ts` — add default color logic for Tag

## Verification

After fixing, the following should all pass:

- TypeScript compilation (`npm run tsc`)
- ESLint (`npm run lint:script`) and Biome lint (`npm run lint:biome`)
- Button unit tests (`--testPathPatterns=button/__tests__/index`)
- Button demo tests (`--testPathPatterns=button/__tests__/demo`)
- Tag unit tests (`--testPathPatterns=tag/__tests__/index`)
- Tag demo tests (`--testPathPatterns=tag/__tests__/demo`)
- Node.js tests (`npm run test:node`)

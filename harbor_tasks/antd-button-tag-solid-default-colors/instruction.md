# Task: Fix Missing Default Colors for Solid Variants

## Problem

When using `variant="solid"` on Button or Tag components without explicitly specifying a `color` prop, the components render without proper color styling. This happens because the solid variant doesn't receive a default color assignment when the color prop is undefined.

## Codebase Context

### Button (`components/button/Button.tsx`)

The Button component is defined as `InternalCompoundedButton` using `React.forwardRef`. It computes a `[color, variant]` pair based on direct props and ConfigProvider context values. The relevant variables in this computation are:

- `variant` / `contextVariant` — the variant from direct props / ConfigProvider context
- `color` / `contextColor` — the color from direct props / ConfigProvider context

The function returns a `[color, variant]` tuple in various cases. When neither a direct color nor a context color is provided, it currently falls through to a default `['default', 'outlined']`, even when the variant is `'solid'`.

### Tag (`components/tag/hooks/useColor.ts`)

The Tag's `useColor` hook resolves color information using:

- `nextVariant` — the resolved variant
- `nextColor` — the resolved color (may be `undefined` when no color prop is given)
- `isPresetColor()` / `isPresetStatusColor()` — utility functions for checking color types

After resolving `nextColor` from the raw `color` prop, the hook checks whether the color is a preset or status color, then determines the final styling.

## Expected Behavior

### Button

When no explicit color is provided and the variant is `'solid'`:

1. When `variant` is `'solid'` and no direct color prop is provided, the component should return the color `'primary'` paired with the variant instead of falling through to the non-solid default
2. When `contextVariant` is `'solid'` and no context color is provided via ConfigProvider, the component should return the color `'primary'` paired with the context variant instead of falling through to the non-solid default
3. Non-solid variants must continue to fall through to their existing default behavior (`['default', 'outlined']`)
4. The component must continue to be defined using `React.forwardRef` and named `InternalCompoundedButton`

### Tag

When no explicit color is provided:

1. The resolved color variable must allow reassignment so it can be updated when default color logic applies
2. When `nextVariant` is `'solid'` and the resolved color is `undefined`, the code should assign `'default'` as the color value before the preset/status checks
3. The preset color check (`isPresetColor`) and status color check (`isPresetStatusColor`) must use the resolved color variable rather than the raw color prop, so they correctly account for any defaulted value
4. Non-solid variants should NOT receive default colors — only `'solid'` variants should

## Files to Modify

- `components/button/Button.tsx` — add default color logic for Button solid variant
- `components/tag/hooks/useColor.ts` — add default color logic for Tag solid variant

## Verification

After fixing, the following should all pass:

- TypeScript compilation (`npm run tsc`)
- ESLint (`npm run lint:script`) and Biome lint (`npm run lint:biome`)
- Button unit tests (`--testPathPatterns=button/__tests__/index`)
- Button demo tests (`--testPathPatterns=button/__tests__/demo`)
- Tag unit tests (`--testPathPatterns=tag/__tests__/index`)
- Tag demo tests (`--testPathPatterns=tag/__tests__/demo`)
- Node.js tests (`npm run test:node`)

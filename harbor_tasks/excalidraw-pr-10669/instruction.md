# Reduce max tablet media query breakpoint and improve UIOptions form factor API

## Problem

Two related issues in the Excalidraw codebase:

1. **Tablet breakpoint too high**: The `MQ_MAX_TABLET` constant in `packages/common/src/editorInterface.ts` is currently set to 1400px. This is too high — it causes small laptops to be incorrectly classified as tablets. The correct value should be 1180px, which matches iPad Air dimensions.

2. **Inflexible form factor API**: The `UIOptions` type in `packages/excalidraw/types.ts` currently accepts a static `formFactor` property, making it impossible to dynamically compute the form factor based on editor dimensions at runtime. Additionally, the `desktopUIMode` property on `UIOptions` is unused and should be cleaned up.

## Desired Behavior

### Media query constants (`packages/common/src/editorInterface.ts`)

- `MQ_MAX_TABLET` should have the value `1180`, with an "iPad Air" comment on the same line
- The `MQ_MIN_WIDTH_DESKTOP` line should include a comment noting it is "not used for form factor detection"
- The relationship `MQ_MIN_TABLET = MQ_MAX_MOBILE + 1` should be preserved

### UIOptions type (`packages/excalidraw/types.ts`)

- The static `formFactor` property should be replaced with a `getFormFactor` callback
- The callback signature: `getFormFactor?: (editorWidth: number, editorHeight: number) => EditorInterface["formFactor"]`
- The `desktopUIMode` property should be removed from `UIOptions`

### App component (`packages/excalidraw/components/App.tsx`)

- The form factor computation should call `UIOptions.getFormFactor` with the editor width and height, falling back to the default implementation when the callback is not provided
- The callback is optional, so optional chaining should be used when invoking it
- All references to `UIOptions.desktopUIMode` should be removed from the editor interface update logic

### Excalidraw component (`packages/excalidraw/index.tsx`)

- The React memo comparison function should handle the `getFormFactor` function property specially — JavaScript functions are compared by reference, so a new function instance on each render would trigger unnecessary re-renders

## Validation

After all changes, the following must pass:

- `yarn test:typecheck` — TypeScript compilation
- `yarn test:code` — ESLint
- `yarn test:other` — Prettier formatting

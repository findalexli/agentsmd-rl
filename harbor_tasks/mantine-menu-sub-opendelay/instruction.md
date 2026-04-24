# Add `openDelay` prop support to Menu.Sub component

## Problem

The `Menu.Sub` component in the Mantine component library supports a `closeDelay` prop to control the delay before closing a submenu on hover, but does not support an `openDelay` prop for controlling the delay before opening. The root `Menu` component already supports `openDelay`, and `Menu.Sub` should have the same capability for consistency.

## Acceptance Criteria

After implementation, the `Menu.Sub` component source file must contain all of the following:

1. The props interface declares the optional numeric prop as: `openDelay?: number;`
2. The default props object includes: `openDelay: 0,`
3. The component function destructures its props using the exact pattern: `const { children, closeDelay, openDelay, ...others }`
4. The hover delay hook call receives the `openDelay` variable reference as `openDelay,` — it must NOT pass a hardcoded value like `openDelay: 0,` to that hook

## Notes

- The Menu component source is located under `packages/@mantine/core/src/components/Menu/`
- Follow existing code patterns and style conventions in the codebase
- The implementation must pass TypeScript type checking and ESLint

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`

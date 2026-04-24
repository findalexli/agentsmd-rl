# Refactor Block Component Export

## Problem

The `Block` component in `packages/solid-router/src/useBlocker.tsx` is currently exported using a deprecated function overload pattern. There is a deprecated standalone function signature for `Block(opts: LegacyPromptProps)` followed by a combined implementation function that handles both `PromptProps` and `LegacyPromptProps`.

The `BlockComponent` interface already specifies both the modern and deprecated signatures. The current separate function overload is redundant and should be consolidated.

## Requirements

Refactor the `Block` component export in `packages/solid-router/src/useBlocker.tsx` to:

1. Use a `const` declaration implementing the `BlockComponent` interface directly
2. Remove the deprecated standalone function overload signature `export function Block(opts: LegacyPromptProps): SolidNode` and its associated JSDoc comment
3. Keep the implementation accepting `PromptProps | LegacyPromptProps` as its parameter type
4. The internal logic of the Block component should remain functionally identical
5. TypeScript must compile without errors after the change

The following types and interfaces in the file must remain unchanged:
- `BlockComponent` interface (already defines the expected signatures)
- `LegacyPromptProps` type (must remain for backward compatibility)
- `PromptProps` type
- `SolidNode` type

The `useBlocker` hook export must also remain unchanged.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`

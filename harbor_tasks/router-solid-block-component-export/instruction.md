# Refactor Block Component Export

## Problem

The `Block` component in `packages/solid-router/src/useBlocker.tsx` is currently exported using a deprecated function overload pattern. There is a deprecated standalone function signature for `Block(opts: LegacyPromptProps)` followed by a combined implementation function that handles both `PromptProps` and `LegacyPromptProps`.

This pattern should be replaced with a single export that implements the existing `BlockComponent` interface directly, which already specifies both the modern and deprecated signatures.

## Requirements

Refactor the `Block` component export in `packages/solid-router/src/useBlocker.tsx` to:

1. Use a `const` declaration with arrow function syntax instead of the current `function` declaration
2. Implement the existing `BlockComponent` interface (which is already defined in the file and specifies both the modern signature and the deprecated legacy signature)
3. Remove the deprecated standalone function overload signature `export function Block(opts: LegacyPromptProps): SolidNode`
4. The implementation must accept `PromptProps | LegacyPromptProps` as its parameter type
5. Use a named function expression for the implementation
6. The internal logic of the Block component should remain functionally identical
7. TypeScript must compile without errors after the change

The following types and interfaces in the file must remain unchanged:
- `BlockComponent` interface (already defines the expected signatures)
- `LegacyPromptProps` type (must remain for backward compatibility)
- `PromptProps` type
- `SolidNode` type

The `useBlocker` hook export must also remain unchanged.

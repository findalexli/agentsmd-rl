# Enhance contextModal functions in @mantine/modals

The `@mantine/modals` package has an inconsistent API for context modals that needs improvement. Currently, the developer experience when using context modals is suboptimal due to inconsistent function signatures and missing functionality.

## What's broken

The context modal API has the following issues:

1. **Inconsistent function signatures**: `openContextModal` uses a different calling convention than other modal functions. It takes the modal key as a separate positional argument `openContextModal(modal: TKey, props: ...)` instead of a single options object.

2. **Missing `closeContextModal`**: There is no dedicated function to close a context modal by its key. The current implementation just calls the regular `closeModal` function, which doesn't properly look up the modal by its context key.

3. **Inconsistent naming**: The hook returns `closeAll` but other functions follow a pattern like `closeModal`, `openModal`. It should be `closeAllModals` for consistency.

4. **Poor TypeScript experience**: The `innerProps` type for context modals is always required, even when the modal doesn't need any inner props. It should be optional when undefined.

## Files to examine

- `packages/@mantine/modals/src/context.ts` - Type definitions and context interface
- `packages/@mantine/modals/src/ModalsProvider.tsx` - Provider component with modal state management
- `packages/@mantine/modals/src/events.ts` - Event system for modals
- `packages/@mantine/modals/src/index.ts` - Public exports
- `packages/@mantine/modals/src/reducer.ts` - State reducer for modals
- `packages/@mantine/modals/src/use-modals/use-modals.test.tsx` - Unit tests

## Expected API contract

### `ModalsContextProps` interface (in `context.ts`)

The context interface should define these members with the following signatures:

- `openContextModal`: generic over `<TKey extends MantineModal>`, accepting a single object parameter containing `modalKey: TKey` (not a separate positional `modal` argument). The old two-argument form `openContextModal(modal: TKey, props: ...)` must not remain in the codebase.
- `closeContextModal`: with signature `closeContextModal: <TKey extends MantineModal>(modalKey: TKey` followed by an optional `canceled` parameter and return type `void`. This replaces the previous version that accepted an `id: TKey`.
- `closeAllModals: () => void` — replaces the previous `closeAll: () => void`.
- `updateContextModal`: generic over `<TKey extends MantineModal>`, accepting `modalKey: TKey` in its props parameter to identify the modal to update.

### Conditional `innerProps` typing (in `context.ts`)

A type named `ContextModalInnerProps` should be defined with conditional logic:
- When the modal's inner props type resolves to empty/undefined: the result should contain `innerProps?: never` (optional property typed as `never`).
- When the modal has actual inner props of type `P`: the result should contain `innerProps: P` (required property).

### `ModalsProvider` (in `ModalsProvider.tsx`)

- Must provide a `closeAllModals` function (not `closeAll`) and include it in the context value as `closeAllModals,`.
- Must include a `closeContextModal` function that looks up the modal ID by matching its context key, then dispatches a close action.

### Event system (in `events.ts`)

- `closeContextModal` must be declared/exported from events.ts.
- The `openContextModal` event handler should reference `modalKey` (not `modal`) in its payload.

### Exports (in `index.ts`)

- `closeContextModal` must be exported from the package's `index.ts`.

### Unit tests (in `use-modals.test.tsx`)

- The `openContextModal` call in tests should use `modalKey: 'contextTest'` in the options object (not a positional argument).
- The test should assert `closeAllModals` is defined on the hook result (not `closeAll`).

## Testing

Run `pnpm test --filter @mantine/modals` to verify your changes work correctly. The TypeScript compiler should also pass without errors.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`

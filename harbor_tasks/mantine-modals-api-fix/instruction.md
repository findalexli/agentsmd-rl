# Fix Breaking Changes in @mantine/modals

The `@mantine/modals` package has accidentally introduced breaking API changes that need to be reverted to restore the original API. The affected source files are in `packages/@mantine/modals/src/`.

## Broken Behaviors

1. **openContextModal signature is wrong**: `openContextModal` currently takes a single object argument with a `modalKey` property to identify the modal. The correct API uses two separate arguments: the modal identifier string as the first argument, and the props object as the second — i.e., `openContextModal(modal: string, { modalId, ...props }: OpenContextModal)`. This two-argument signature must be reflected in both the function implementation and the type definition in the context interface. Note that the events system dispatches single-object payloads containing a `modal` property, which needs to be reconciled with the two-argument function signature when events are handled by the provider.

2. **closeAllModals vs closeAll naming**: The `ModalsContextProps` interface exposes a method called `closeAllModals`, but the correct name in the context interface is `closeAll`. The events layer should continue using `closeAllModals` as its event name — only the context interface and provider internals should use `closeAll`.

3. **updateContextModal requires unnecessary modalKey**: `updateContextModal` currently requires both `modalKey` and `modalId` in its destructured parameters. Only `modalId` and the remaining props are needed.

4. **ContextModalInnerProps type should not exist**: A `ContextModalInnerProps` helper type exists in the type definitions but is unnecessary and should be removed. `OpenContextModal` should be a simple interface without this helper.

5. **closeContextModal is needlessly different from closeModal**: `closeContextModal` should behave identically to `closeModal`. It also should not be exported from the package's public entry point (`index.ts`).

6. **MantineModals type augmentation is broken**: The `MantineModals` type does not properly support type augmentation via declaration merging. It needs a `MantineModalsOverwritten` type that integrates with the `MantineModalsOverride` interface for proper type inference.

7. **OpenContextModal generic parameter**: References to `OpenContextModal` in the codebase should use an explicit generic parameter (`OpenContextModal<any>`) where a specific type is not available, to ensure type compatibility.

## Verification

After applying fixes, the following should all pass:
- TypeScript compilation (`npx tsc --noEmit --project tsconfig.json` in the modals package)
- Jest tests (`npx jest packages/@mantine/modals --no-coverage`)
- ESLint (`npx eslint packages/@mantine/modals/src --no-cache`)
- Prettier (`npx prettier --check "packages/@mantine/modals/**/*.{ts,tsx}"`)

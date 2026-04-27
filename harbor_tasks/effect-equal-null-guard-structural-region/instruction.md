# Fix `Equal.equals` crash on null inside `Utils.structuralRegion`

## Repository

You are working in a clone of the [Effect-TS/effect](https://github.com/Effect-TS/effect) monorepo at `/workspace/effect`. The relevant package is `packages/effect`.

## Symptom

`Equal.equals` from the `effect` package crashes with `TypeError: Cannot convert undefined or null to object` whenever it is called inside a `Utils.structuralRegion` and one (but not both) of the operands is `null`.

The crash is reproducible in a TypeScript file that simply imports the public `effect` package from this monorepo:

```ts
import { Equal, Utils } from "effect"

Utils.structuralRegion(() => {
  Equal.equals({ name: "hello" }, null)
})
// TypeError: Cannot convert undefined or null to object
```

## Expected behavior

Inside a `Utils.structuralRegion(...)` block, `Equal.equals` must:

1. **Never throw** when comparing any combination where one operand is `null`. This includes:
   - `Equal.equals(null, { a: 1 })` and `Equal.equals({ a: 1 }, null)`
   - `Equal.equals(null, [1, 2, 3])` and `Equal.equals([1, 2, 3], null)`
2. Return `false` whenever exactly one of the two operands is `null` and the other is a non-null object, array, or any other value.
3. Return `true` for `Equal.equals(null, null)` (already correct today).
4. Return `false` for `Equal.equals(null, "hello")`, `Equal.equals(null, undefined)` and any other primitive-vs-null mismatch (already correct today).
5. Continue to recurse correctly into nested objects whose leaf values may be `null`. Two structurally identical nested objects with `null` leaves must compare equal; a `null` leaf vs a non-null leaf at the same key must compare not-equal — without throwing.

The same behavior must hold outside a `structuralRegion`, where it already works.

## What is broken

Inside a structural region, the structural-comparison code path is reached for `(null, object)` pairs (since `typeof null === "object"`) but does not handle `null` before performing operations that require a real object. Trace `Equal.equals` for the inputs above to find where this fails, and prevent the crash.

You must not change the public API of `Equal.equals` or `Utils.structuralRegion` — only the internal behavior so that the cases above stop throwing and return the correct boolean.

## Repository conventions

Follow the project conventions documented in `AGENTS.md` at the repository root. In particular:

- All pull requests must include a changeset entry in the `.changeset/` directory. Add a new `.md` file there bumping the `effect` package (a `patch` bump is appropriate for a bug fix). Look at existing files in `.changeset/` (for example `.changeset/huge-peaches-jump.md`) to see the expected format.
- `index.ts` files under `packages/*/src/` are automatically generated barrel files and must not be edited by hand.
- If you create any temporary debugging files in the `scratchpad/` directory, delete them when you are done.
- Choose clear, maintainable solutions over clever ones; keep changes concise; avoid adding explanatory comments unless the logic is genuinely non-obvious.

## Code Style Requirements

The repository's automated checks must continue to pass after your change:

- **ESLint** must pass on `packages/effect/src/Equal.ts`. Run `pnpm lint packages/effect/src/Equal.ts` (or `pnpm lint-fix` to auto-format) before finishing.
- **Vitest** suite for `packages/effect/test/Equal.test.ts` must continue to pass.

## Verifying your work

The repo already has a working `pnpm install` and `pnpm exec tsx` available. You can write a small TypeScript reproduction in `scratchpad/` and run it with `pnpm exec tsx scratchpad/your-file.ts` to confirm the crash before the fix and the correct boolean returns after, then delete the file when you are done.

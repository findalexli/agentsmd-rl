# Effect Schema: `getPropertySignatures` crashes on `Struct` with `optionalWith({ default })`

The Effect repository (`Effect-TS/effect`) lives at `/workspace/effect`. You are working at base commit `ab3b64c20a039eb4d573fe757c41278925b22687` on the `effect` package (`packages/effect`).

## The bug

Calling `AST.getPropertySignatures` on a `Schema.Struct` that contains a field declared with `Schema.optionalWith(..., { default: () => ... })` throws:

```
Error: Unsupported schema (Transformation)
```

The crash also reproduces with the other `optionalWith` option variants that produce a `Transformation` AST node — for example `{ as: "Option" }` and `{ nullable: true, default: () => ... }`.

A minimal repro using the public API is:

```ts
import * as S from "effect/Schema"
import * as AST from "effect/SchemaAST"

const schema = S.Struct({
  a: S.String,
  b: S.optionalWith(S.Number, { default: () => 0 })
})

AST.getPropertySignatures(schema.ast)
// throws: Error: Unsupported schema (Transformation)
```

The same call on a non-Transformation Struct works fine — only `optionalWith`-flavoured variants (and any other API path that wraps the field type in a `Transformation` AST node) trigger it.

## Expected behaviour

`AST.getPropertySignatures` should return one `PropertySignature` per declared key, exactly as it does for plain Structs. For the example above:

- The result should be an array of length `2`.
- The first signature has `name === "a"`.
- The second signature has `name === "b"`.

The fix should also handle the `{ as: "Option" }` and `{ nullable: true, default: ... }` variants, and must not regress plain (non-Transformation) Structs.

## Where to look

`packages/effect/src/SchemaAST.ts` defines several AST-walking helpers. Two of them — `getPropertyKeyIndexedAccess` and `getPropertyKeys` — share a common shape: a `switch` over `ast._tag` with cases for `TypeLiteral`, `Union`, `Suspend`, `Refinement`, etc., and a fallback `throw new Error(...Unsupported schema...)`.

`getPropertySignatures` is itself implemented (on the fallback path) as `getPropertyKeys(ast).map(name => getPropertyKeyIndexedAccess(ast, name))`. So if `getPropertyKeys` knows how to walk a given `_tag` but `getPropertyKeyIndexedAccess` does not, the first half succeeds and the second half throws — which is exactly what's happening here.

Compare the two helpers and bring them into agreement for the missing AST node tag. The fix should mirror the pattern used by the existing `Suspend` and `Refinement` arms (a one-line delegating `return`), not introduce a new helper.

## What to deliver

1. A fix in `packages/effect/src/SchemaAST.ts` that resolves the crash for all `optionalWith` variants that produce a `Transformation` AST node, without regressing plain Structs.
2. A `.changeset/*.md` entry describing the fix. The repo's `AGENTS.md` requires this for every PR. The frontmatter should bump the `effect` package (e.g. `"effect": patch`), and the body should clearly mention what was fixed (the `getPropertySignatures` / `Transformation` / `optionalWith` interaction).

## Repository conventions

The repository's `AGENTS.md` (at the repo root) is authoritative — read it. In particular:

- Package manager is **`pnpm`** (version pinned via `corepack`).
- Run `pnpm lint-fix` after editing files.
- Run tests with `pnpm test run <test_file.ts>` (vitest under the hood).
- Run `pnpm check` for type checking.
- "Avoid comments unless absolutely required to explain unusual or complex logic."
- "Always look at existing code in the repository to learn and follow established patterns before writing new code."
- Tests use `describe`/`it` + `deepStrictEqual` from `@effect/vitest`, not vitest's `expect`.

## Code Style Requirements

The grader runs the repo's own type checker (`pnpm check` → `tsc -b tsconfig.json`) inside `packages/effect`. Your fix must compile cleanly. ESLint cleanliness is also expected per `AGENTS.md` — run `pnpm lint-fix` before declaring done.

## Out of scope

- `getIndexSignatures` has a separate (silent) symptom on the same AST node; do **not** fix it as part of this task.
- The `@effect/ai` package's downstream consumers (`Tool.getJsonSchema`, `LanguageModel.streamText`) call into `getPropertySignatures`; they do not need direct edits — fixing the underlying helper is sufficient.
- Don't refactor surrounding code or touch unrelated `_tag` arms.

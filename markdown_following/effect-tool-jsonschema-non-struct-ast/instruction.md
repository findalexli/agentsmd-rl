# Fix `Tool.getJsonSchemaFromSchemaAst` for non-struct AST inputs

The repository is a pnpm monorepo. The package you need to edit lives at
`packages/ai/ai/` (published as `@effect/ai`).

## Repro

From `packages/ai/ai/`, run this script with `tsx`:

```ts
import * as Schema from "effect/Schema"
import * as Tool from "@effect/ai/Tool"

console.log(JSON.stringify(Tool.getJsonSchemaFromSchemaAst(Schema.Number.ast as any)))
console.log(JSON.stringify(Tool.getJsonSchemaFromSchemaAst(Schema.String.ast as any)))
console.log(JSON.stringify(Tool.getJsonSchemaFromSchemaAst(Schema.Boolean.ast as any)))
```

## Observed

Every call returns the same placeholder object schema:

```json
{"type":"object","properties":{},"required":[],"additionalProperties":false}
```

regardless of whether the input AST describes a number, string, boolean, or
anything else that is not a struct. The placeholder is wrong: a primitive
AST should map to a primitive JSON Schema.

## Expected

`Tool.getJsonSchemaFromSchemaAst` must forward every AST it receives to
`JsonSchema.fromAST` so that the resulting JSON Schema reflects the actual
shape of the input. After your fix:

- `Schema.Number.ast` produces a JSON Schema with `type: "number"`.
- `Schema.String.ast` produces a JSON Schema with `type: "string"`.
- `Schema.Boolean.ast` produces a JSON Schema with `type: "boolean"`.
- A `Schema.Struct({...})` AST continues to produce an object schema with
  the correct `properties` and `required` fields (no regression).
- A `Schema.Struct({ name: Schema.String, count: Schema.optionalWith(Schema.Number, { default: () => 10 }) })`
  AST still produces an object schema where `name` is required and `count`
  is in `properties` but **not** in `required`.

## Where to look

The function `getJsonSchemaFromSchemaAst` is exported from
`packages/ai/ai/src/Tool.ts`. Its current implementation uses
`AST.getPropertySignatures` to decide whether the input is "object-shaped"
and falls back to a hard-coded empty-object schema when that returns no
properties. That heuristic discards the actual AST instead of delegating
to the JSON Schema generator. `JsonSchema.fromAST` (already imported in the
same file) handles every supported AST kind directly.

## Constraints

- Do **not** alter the public signature of `getJsonSchemaFromSchemaAst` or
  of `getJsonSchema`.
- Do **not** modify any file under `packages/effect/` — the upstream Schema
  AST utilities are correct as-is.
- The existing `@effect/ai` Tool test suite must continue to pass:
  `pnpm --filter=@effect/ai test run Tool.test.ts`.

## Repo workflow

This is the Effect monorepo. The root `AGENTS.md` documents the contributor
workflow. Read it before you start. In particular:

- Use `pnpm` as the package manager.
- All pull requests must include a changeset in the `.changeset/` directory.
  Add a new `.changeset/<slug>.md` file describing your change for the
  `@effect/ai` package.
- Keep code and any wording concise. Reduce comments — only add a comment
  if it explains something genuinely non-obvious.
- Follow established patterns in the surrounding code; do not introduce
  new abstractions.

## Code Style Requirements

- Lint and type-check are part of the repo's CI. If you add or remove code,
  make sure it still passes:
  - `pnpm --filter=@effect/ai check` — TypeScript type check.
  - `pnpm lint` — ESLint (the repo uses `pnpm lint-fix` to auto-format).

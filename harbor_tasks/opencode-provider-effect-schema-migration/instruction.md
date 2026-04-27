# Migrate the provider domain from zod to Effect Schema

This repo (`packages/opencode`) is in the middle of moving its domain models
from `zod` to Effect Schema as the canonical source of truth, with `zod`
retained only as a derived compatibility surface (`.zod` statics, the
`@/util/effect-zod` walker, and `@/util/named-schema-error` for typed
errors).

The progress tracker lives at
`packages/opencode/specs/effect/schema.md`. Read it — the migration rules,
preferred shapes, and progress log are all there.

The provider domain is the next slice. The tracker currently lists three
files under **Provider domain** as incomplete:

- `packages/opencode/src/provider/auth.ts`
- `packages/opencode/src/provider/models.ts`
- `packages/opencode/src/provider/provider.ts`

Your job: complete that slice.

## What "done" means for each file

A file is done when its exported schema/error values are authored as Effect
Schema (using `Schema.Struct`, `Schema.Record`, `Schema.optional`,
`Schema.Union`, `Schema.Literals`, etc., from `effect`), inferred types are
derived with `Schema.Schema.Type<typeof X>`, and the file no longer carries
an `import ... from "zod"` line. The compatibility helpers
(`zod(...)` from `@/util/effect-zod`, `withStatics(...)` from
`@/util/schema`) may still be used to expose a `.zod` static where existing
zod consumers depend on it.

For the typed errors specifically, use the existing
`namedSchemaError(tag, fields)` helper from
`packages/opencode/src/util/named-schema-error.ts`. It is a drop-in
replacement for `NamedError.create(tag, zodShape)`: the wire shape and
runtime API stay byte-identical, but the source of truth is now an Effect
`Schema.Struct`. Read the helper before using it — it documents exactly
what surface it preserves.

After the source files are migrated, update
`packages/opencode/specs/effect/schema.md` so the three provider files are
checked off (`- [x]` instead of `- [ ]`) under the **Provider domain**
section.

## Constraints

- The package must still typecheck. Run `bun typecheck` from
  `packages/opencode` (the repo's `AGENTS.md` is firm: never run `tsc`
  directly, never run typecheck or tests from the repo root).
- The recursive `JsonValue` shape in `models.ts` is a known footgun:
  `Types.DeepMutable` widens it into a TS2589 (recursive depth limit) on
  this project's compiler. Keep the inferred Schema types as
  `Schema.Schema.Type<...>` (which is `readonly`) rather than introducing
  a `DeepMutable` over it. Adjust call sites that need a mutable array
  instead — for instance, in `provider.ts`'s `fromModelsDevProvider`,
  spread `provider.env ?? []` into a fresh array rather than widening the
  schema's type.
- Domain values, IDs, and shapes must remain wire-compatible — the
  generated SDK output should be byte-identical (this is the whole reason
  `effect-zod` and `namedSchemaError` exist).
- Do **not** delete or modify `@/util/effect-zod` or
  `@/util/named-schema-error` themselves; they are the compatibility layer
  the tracker explicitly keeps.

## Style

Follow the repo style guide in `AGENTS.md` and
`packages/opencode/AGENTS.md`. Most of it ports directly from the existing
provider code: avoid `try`/`catch`, avoid `any`, prefer `const`,
prefer early returns, prefer dot notation over destructuring, inline
single-use values.

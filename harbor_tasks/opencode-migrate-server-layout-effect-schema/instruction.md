# Migrate Server and Layout config to Effect Schema

The repository is `opencode`, a TypeScript/Bun monorepo. The relevant package
lives at `packages/opencode/` and uses the `effect` v4-beta library along with
its `Schema` module for typed configuration. The repository is in the middle
of an incremental migration: legacy config schemas are written using `zod`
directly (`z.object(...)`, `z.enum(...)`), while newer ones are authored with
`Schema` from `effect` and exposed to legacy consumers through a `.zod`
accessor produced by the in-tree `zod()` walker (`@/util/effect-zod`) and
`withStatics` helper (`@/util/schema`).

`packages/opencode/src/config/config.ts` still defines two schemas inline:
`Server` and `Layout`. Both need to be migrated to standalone modules under
`packages/opencode/src/config/`, following the same pattern that the existing
sibling modules use (e.g. `packages/opencode/src/config/agent.ts`,
`packages/opencode/src/config/permission.ts`,
`packages/opencode/src/config/provider.ts`).

## What the new modules must look like

Create two new files in `packages/opencode/src/config/`:

- `layout.ts` — defines `Layout` as an Effect `Schema` accepting the literal
  string values `"auto"` and `"stretch"` only. The schema must carry an
  `identifier` annotation of `"LayoutConfig"` so JSON-Schema generation keeps
  the same `$ref` name as before. It must expose a `.zod` static that returns
  the equivalent `zod` schema (use `zod()` from `@/util/effect-zod` plus
  `withStatics` from `@/util/schema`). Also export the `Layout` *type* as
  `Schema.Schema.Type<typeof Layout>`. The file must self-export its public
  members under the namespace name `ConfigLayout`.

- `server.ts` — defines a `Server` Effect schema with the same shape as the
  current `z.object(...)` definition in `config.ts`:
  - `port`: optional positive integer (must reject zero, negatives, and
    non-integers)
  - `hostname`: optional string
  - `mdns`: optional boolean
  - `mdnsDomain`: optional string
  - `cors`: optional array of strings
  Each field must keep its existing `description` annotation. The Effect
  identifier must be `"ServerConfig"` so generated JSON Schema keeps the
  same `$ref` name. Expose a `.zod` static returning the equivalent zod
  schema. The file must self-export its public members under the namespace
  name `ConfigServer`.

## What `config.ts` must do after the migration

After migration, `packages/opencode/src/config/config.ts` must:

- Import `ConfigLayout` from `./layout` and `ConfigServer` from `./server`.
- Re-export `Server` as `ConfigServer.Server.zod` so that the rest of the
  codebase (which imports `Config.Server` and feeds it to `zod` parsers)
  keeps working unchanged.
- Re-export `Layout` as `ConfigLayout.Layout.zod` for the same reason, and
  re-export the `Layout` *type* as `ConfigLayout.Layout`.
- Drop the legacy inline `z.object({ ... }).strict().meta({ ref: "ServerConfig" })`
  and `z.enum(["auto", "stretch"]).meta({ ref: "LayoutConfig" })` definitions.
- The exact behavior visible to callers (validation rules, JSON-Schema
  identifiers) must be identical before and after the migration.

## Cleanup in `provider.ts`

`packages/opencode/src/config/provider.ts` currently carries a stale
explanatory comment block immediately above the `PositiveInt` definition that
references the `ZodOverride` walker. That comment is no longer accurate after
recent walker changes and should be removed (the `PositiveInt` definition
itself stays unchanged).

## Behavior to preserve

The `.zod` schema returned by `ConfigServer.Server.zod` must behave like the
current inline `Server` zod schema:

- Accept an empty object (all fields optional).
- Accept a fully-populated object such as
  `{ port: 3000, hostname: "localhost", mdns: true, mdnsDomain: "opencode.local", cors: ["https://example.com"] }`.
- Reject a `port` of `0`, a negative `port`, or a non-integer `port` such as
  `3.5`.
- Reject `hostname` values that are not strings.
- Reject `cors` values that are not arrays of strings.

The `.zod` schema returned by `ConfigLayout.Layout.zod` must accept exactly
the strings `"auto"` and `"stretch"` and reject everything else (including
the empty string).

## Constraints from project AGENTS.md

- `packages/opencode/AGENTS.md` mandates Effect's `Schema.Class` for
  multi-field data — use it for `Server` rather than `Schema.Struct`.
- The same file forbids `export namespace Foo { ... }` for module
  organization; use top-level exports plus an `export * as Config<X>`
  self-reexport instead.
- The root `AGENTS.md` requires the self-reexport pattern for new
  modules added under `src/config`.
- Avoid the `any` type; rely on type inference where possible.
- Prefer `const` and early returns over `let` and `else`.

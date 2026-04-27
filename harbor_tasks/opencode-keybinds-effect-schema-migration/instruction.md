# Migrate `keybinds.ts` to Effect Schema

The opencode codebase is in the middle of migrating its config schemas from
direct `zod` declarations onto `effect`'s `Schema` module. A previous change
landed a `zod()` walker (`packages/opencode/src/util/effect-zod.ts`) that
consumes an `Effect` schema's AST and emits an equivalent runtime `ZodType`,
so the consumer surface stays unchanged while the source of truth becomes
Effect.

Your job is to migrate `packages/opencode/src/config/keybinds.ts` onto Effect
Schema using that walker.

## What the consumers rely on

`Keybinds` is a TUI-internal schema. The places in the rest of the package
that need to keep working unchanged are:

- `Keybinds.shape` — iterated in `packages/opencode/src/cli/cmd/tui/config/tui-schema.ts`
  to build the partial-override schema. All keybind keys must still appear
  here.
- `Keybinds.parse(input)` — called in
  `packages/opencode/src/cli/cmd/tui/config/tui.ts` to fill in defaults from
  the user's config.
- `Keybinds.shape.<field>.parse(undefined)` — `tui.ts` uses this exact
  expression to pull a single field's default value before merging the user
  override.

Every existing keybind field, every existing default, and the `KeybindsConfig`
identifier annotation must survive the migration.

## Two simplifications that should also happen

While translating the schema, fold these in too:

1. **`terminal_suspend` no longer needs its `.transform(...)`.** The current
   declaration is `.default("ctrl+z").transform((v) => process.platform === "win32" ? "none" : v)`.
   Look at the consumer in `tui.ts` — before `Keybinds.parse(...)` runs, the
   surrounding code already unconditionally sets `keybinds.terminal_suspend = "none"`
   on win32, so the schema-level platform branch is dead code. Drop the
   transform; the field becomes a plain default of `"ctrl+z"`.

2. **The top-level schema should not be strict.** The user-facing
   `KeybindOverride` schema in `tui-schema.ts` is already strict, so unknown
   keybind keys are rejected upstream before they ever reach this layer. As
   a result, after the migration `Keybinds.parse({ leader: "ctrl+x", some_unknown_key: "x" })`
   should not throw — unknown keys can be silently dropped at this layer.

## Behavior expected of the migrated schema

When the migration is correct, on Linux:

- `Object.keys(Keybinds.shape).length === 97`
- `Keybinds.parse({}).leader === "ctrl+x"`
- `Keybinds.parse({}).editor_open === "<leader>e"`
- `Keybinds.parse({}).terminal_suspend === "ctrl+z"`
- `Keybinds.shape.input_undo.parse(undefined) === "ctrl+-,super+z"`
- `Keybinds.parse({ leader: "ctrl+x", _unknown_key_xyz: "blah" })` returns an
  object whose `leader` is `"ctrl+x"` (it does **not** throw)

## Notes / hints

- The `zod()` walker in `@/util/effect-zod` already understands
  `Schema.String.pipe(Schema.optional, Schema.withDecodingDefault(Effect.succeed(default)))`
  and emits `z.string().default(default)` for it. That is the canonical way
  to express "optional string with a default" on the Effect side.
- The `description` annotation on each field should round-trip into the
  corresponding zod field's `.describe(...)`.
- `Schema.Struct(...).annotate({ identifier: "KeybindsConfig" })` is the
  Effect equivalent of `.meta({ ref: "KeybindsConfig" })`.
- The runtime type returned by `zod(KeybindsSchema)` is a `ZodObject`, but
  the static type is `ZodType` — the export needs a cast (`as unknown as
  z.ZodObject<...>`) so consumers that touch `.shape` typecheck. Type-only
  imports of `zod` are fine for that.
- The exact platform-conditional default on `input_undo` must be preserved,
  since on Windows it differs from Linux/macOS.

## Code Style Requirements

The repo's `AGENTS.md` style guide applies. Most relevant here:

- Avoid `try`/`catch`.
- Avoid `any`.
- Prefer `const` and ternaries over `let` and reassignment.
- Avoid `else` after a return — use an early return.
- Inline single-use values rather than introducing extra `const` bindings.
- Avoid unnecessary destructuring.
- The existing self-export pattern at the top of `src/config/*.ts`
  (e.g. `export * as ConfigKeybinds from "./keybinds"`) must remain.

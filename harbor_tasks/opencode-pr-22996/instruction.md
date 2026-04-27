# Split `ConfigParse` into explicit JSONC and schema steps

You are working in the [opencode](https://github.com/anomalyco/opencode) monorepo. Run `bun` commands from `packages/opencode/`, not the repo root.

## The current shape

`packages/opencode/src/config/parse.ts` today exports two combined entry points under the `ConfigParse` namespace:

- `ConfigParse.parse(schema, text, filepath)` — parses `text` as JSONC and validates against `schema` in one call.
- `ConfigParse.load(schema, text, options)` — additionally calls `ConfigVariable.substitute(...)` to expand `{env:...}` / `{file:...}` tokens before parsing, accepts an optional `normalize` callback that runs between the JSONC parse and the schema validation, and supports a `missing: "error" | "empty"` flag.

`ConfigVariable.substitute` is currently a positional function: `substitute(text, input, missing)`, where `input` is the `ParseSource` discriminator (`{ type: "path", path }` or `{ type: "virtual", source, dir }`).

## What you must change

### `ConfigParse` should expose two smaller, explicit steps

Replace the combined `parse` and `load` exports with two new functions:

- `ConfigParse.jsonc(text: string, filepath: string): unknown`
  - Parses `text` as JSONC (still accepting trailing commas and comments) and returns the resulting raw value.
  - On parse errors, throws a `JsonError` (already defined in the local `./error` module) whose message includes the same line/column information that the existing combined function produces today.
  - Performs **no** schema validation and **no** variable substitution.

- `ConfigParse.schema<T>(schema: z.ZodType<T>, data: unknown, source: string): T`
  - Runs `schema.safeParse(data)` and returns the parsed value on success.
  - On failure, throws an `InvalidError` (already defined in the local `./error` module) with `path: source` and `issues` set to the zod issues.
  - Does **not** parse JSONC. The caller is expected to pass already-parsed data (e.g. the return value of `ConfigParse.jsonc`, or data produced by some other source such as the existing managed-config plist parser).

Remove `ConfigParse.parse`, `ConfigParse.load`, and the `LoadOptions` type entirely from `parse.ts`. The `ConfigVariable` import and any helper that only existed to support `load` should also go (the line/column formatting helper can be inlined into `jsonc`).

### `ConfigVariable.substitute` should take a single options object

Change the export to:

- `substitute(input: SubstituteInput): Promise<string>`
- where `SubstituteInput` extends the existing `ParseSource` with `text: string` and `missing?: "error" | "empty"` (default `"error"`).

The substitution behavior is otherwise unchanged: `{env:VAR}` is replaced by `process.env[VAR] || ""`; `{file:...}` is replaced by the referenced file's text content (lines whose trimmed prefix begins with `//` are still skipped); `missing: "empty"` still causes missing referenced files to substitute the empty string instead of throwing.

### Update every caller

Every caller of the old `ConfigParse.load` / `ConfigParse.parse` and of the old positional `ConfigVariable.substitute(text, input, missing)` — including any tests in this package that used them — must be updated to the new shape. The natural rewrite is the explicit pipeline `substitute → jsonc → (caller-specific normalization) → schema`. Do not introduce a new combined wrapper to recreate the old `load`. Each caller should own its own substitution and normalization steps explicitly.

The refactor must preserve all observable behavior: end-user config loading, the TUI config loader, and the managed-plist tests must all continue to behave identically.

## Code Style Requirements

- Follow the project conventions in `AGENTS.md`: no `try`/`catch` unless necessary, prefer early returns, no `else` after `return`, use `const`, avoid `any`, and rely on type inference. Do not add explicit type annotations or interfaces beyond what is required for the exported function signatures listed above.
- The repository uses Prettier with `semi: false` and `printWidth: 120`. Match existing formatting.
- Keep the existing `export * as ConfigParse from "./parse"` and `export * as ConfigVariable from "./variable"` self-export pattern at the top of each file.

## How to verify locally

From `packages/opencode/`:

```
bun test test/config/config.test.ts
```

should still produce all green tests.

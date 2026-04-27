# Split the formatter and lsp config schemas into dedicated modules

The opencode CLI lives in this repo as a Bun + TypeScript monorepo. Its
top-level configuration object is assembled in
`packages/opencode/src/config/config.ts` from many domain-specific Zod
schemas. Most of those schemas already live in their own files inside
`packages/opencode/src/config/` (e.g. `agent.ts`, `permission.ts`,
`provider.ts`, `skills.ts`); they are then composed together inside
`config.ts`. Two schemas — the **formatter** schema and the **lsp**
schema — were left inline in `config.ts` and have not been factored out
yet. Your task is to bring them in line with the rest of the
`src/config` directory.

## What needs to change

### 1. Create two new modules under `packages/opencode/src/config/`

- A `formatter` module containing the schema currently inlined under the
  `formatter:` field of `config.ts`'s top-level `Info` schema. It must
  export a `Info` Zod schema whose accepted root values are:
  - the literal `false` (formatters disabled), or
  - a record (`Record<string, …>`) keyed by formatter id, where each
    value is an object with these optional fields: `disabled: boolean`,
    `command: string[]`, `environment: Record<string, string>`, and
    `extensions: string[]`.

  It must also export the corresponding inferred `type Info`.

- An `lsp` module containing the schema currently inlined under the
  `lsp:` field of `config.ts`'s top-level `Info` schema. It must export
  a `Info` Zod schema whose accepted root values are:
  - the literal `false` (LSP disabled), or
  - a record keyed by LSP server id whose entries are either
    `{ disabled: true }`, or an object with `command: string[]` and
    optional `extensions: string[]`, `disabled: boolean`,
    `env: Record<string, string>`, `initialization: Record<string, any>`.

  It must also preserve the **custom-server refinement**: a config under
  any id that is *not* one of the built-in LSP server ids in
  `packages/opencode/src/lsp/server.ts` must be rejected unless either
  `disabled: true` or an `extensions` array is present. The refinement
  message must be the string
  `For custom LSP servers, 'extensions' array is required.`. As before,
  the schema must read the known server ids from
  `import * as LSPServer from "../lsp/server"` and treat each export's
  `.id` as a known id. The `false` (disable-all) value bypasses the
  refinement.

  The module must also export the inferred `type Info`.

### 2. Wire the new modules into the existing config

- `packages/opencode/src/config/config.ts` must no longer carry the
  inline `formatter`/`lsp` schemas, and must no longer import
  `LSPServer` directly — both responsibilities now live in the new
  modules. The `Info` schema's `formatter` and `lsp` fields should be
  built from the new modules' exported `Info` schemas (preserving the
  `.optional()` modifier they already have).

- `packages/opencode/src/config/index.ts` must re-export the two new
  modules as namespaces alongside the other `Config*` re-exports.

### 3. Document the convention in the agent-instruction files

The repository already keeps two `AGENTS.md` files that codify
conventions for code agents working in this tree:

- the root-level `AGENTS.md`, and
- `packages/opencode/AGENTS.md`.

Both must be updated to spell out, in their own words, the
**self-export convention** for files in `src/config`: each module in
that directory begins (at the top of the file) with a self-export of
its own namespace, e.g. `export * as ConfigAgent from "./agent"`. New
config modules must follow the same pattern.

The new wording in each file must mention `src/config`, the
"self-export" idea, and include the `export *` form of the example so
that a reader new to the repo can copy the pattern without having to
look at sibling files. In `packages/opencode/AGENTS.md`, place the rule
under a new section heading appropriate for module-level conventions
(it is not a schemas-and-errors rule, nor an Effect rule).

## Code Style Requirements

This repo's `AGENTS.md` codifies several style rules that apply to any
new code you write here. Of particular relevance for the new modules:

- Use type inference where possible; avoid explicit type annotations
  except where required for export.
- Prefer functional array methods (`flatMap`, `filter`, `map`) over
  `for` loops where the original code used them.
- Reduce variable count by inlining single-use values.

There is no separate linter step in this task — but the repo's
`bun typecheck` (run from a package directory) is the authoritative
check the maintainers use, so the new modules must remain
type-correct against the existing `config.ts` consumers.

## Hints

- Follow the pattern already established in sibling modules such as
  `packages/opencode/src/config/agent.ts`,
  `packages/opencode/src/config/permission.ts`, and
  `packages/opencode/src/config/skills.ts` for how the file should be
  laid out (self-export at top, then `import z from "zod"`, then
  exported schemas).
- Take care not to change the **observable parsing behavior** of the
  formatter or lsp configs — the goal here is purely to relocate the
  schemas. The full opencode config (`Info` in `config.ts`) must still
  accept the same documents it accepted before.

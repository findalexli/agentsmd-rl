# Vendor and simplify the `minimist` argument parser in cli-client

The `playwright-core` cli-client currently consumes the `minimist` npm package
(via `require('minimist')` in `packages/playwright-core/src/tools/cli-client/program.ts`)
plus the `@types/minimist` dev dependency for TypeScript types. The wrapper
code in program.ts then post-processes the parsed result to enforce a few
project-specific rules.

You need to **replace this external dependency with a self-contained, vendored
TypeScript implementation** that integrates the project-specific rules
directly into the parser, and remove the `@types/minimist` devDependency.

## What to deliver

1. A new TypeScript source file at
   `packages/playwright-core/src/tools/cli-client/minimist.ts` that exports:

   - A `minimist(args: string[], opts?: MinimistOptions): MinimistArgs`
     function that parses a Unix-style argv array.
   - A `MinimistOptions` type with two optional members: `string` and
     `boolean`, each accepting either a single string or an array of strings
     (the names of options to be treated as string-typed or boolean-typed).
   - A `MinimistArgs` type whose shape is
     `{ _: string[]; [key: string]: string | boolean | string[] | undefined }`.

2. Update `packages/playwright-core/src/tools/cli-client/program.ts` and
   `packages/playwright-core/src/tools/cli-client/session.ts` to import
   `minimist` and the `MinimistArgs` type from the new module instead of
   declaring their own `type MinimistArgs` and using `require('minimist')`.
   The previous post-processing block in program.ts that ran after
   `require('minimist')(...)` should be removed — its responsibilities now
   belong to the vendored parser itself.

3. Update `packages/playwright-core/src/tools/cli-client/DEPS.list` so that
   `program.ts` and `session.ts` are allowed to import `./minimist.ts`, and
   add a section for the new file.

4. Remove `@types/minimist` from the root `package.json` `devDependencies`
   (the npm package itself is no longer imported either).

## Required parser behaviors

The vendored parser implements only the subset of `minimist` actually used by
the cli-client. It must support the following inputs and produce these
outputs (no aliases, no defaults, no `stopEarly`, no dot-notation keys, no
unknown-callback — those features are intentionally dropped). All examples
below assume `args` is the second argument to `process.argv` slicing
(i.e. the array shown).

| Input `args` | `opts` | Result |
|---|---|---|
| `["--foo=bar"]` | `{}` | `{ _: [], foo: "bar" }` |
| `["--foo", "bar"]` | `{}` | `{ _: [], foo: "bar" }` |
| `["--foo"]` | `{}` | `{ _: [], foo: true }` |
| `["--no-foo"]` | `{}` | `{ _: [], foo: false }` |
| `["alpha", "beta", "gamma"]` | `{}` | `{ _: ["alpha", "beta", "gamma"] }` |
| `["-x"]` | `{}` | `{ _: [], x: true }` |
| `["--tag", "a", "--tag", "b", "--tag", "c"]` | `{}` | `{ _: [], tag: ["a","b","c"] }` |
| `["--foo", "bar", "--", "baz", "--qux", "quux"]` | `{}` | `{ _: ["baz","--qux","quux"], foo: "bar" }` |
| `["cmd", "--opt", "val", "extra"]` | `{}` | `{ _: ["cmd","extra"], opt: "val" }` |
| `["--name"]` | `{ string: ["name"] }` | `{ _: [], name: "" }` |
| `[]` | `{ boolean: ["foo"] }` | `{ _: [] }` &nbsp;(`foo` must be **absent**, not `false`) |
| `["--no-enabled"]` | `{ boolean: ["enabled"] }` | `{ _: [], enabled: false }` |
| `["--enabled", "true"]` | `{ boolean: ["enabled"] }` | `{ _: [], enabled: true }` |
| `["--enabled", "false"]` | `{ boolean: ["enabled"] }` | `{ _: [], enabled: false }` |

### Boolean-with-equals must throw

When a name listed in `opts.boolean` is passed in `--name=value` form, the
parser must throw an `Error` whose message contains the substring
`should not be passed with '=value'` and includes `--<name>` so the caller
sees which option was misused. (Equivalent rule in the original program.ts
post-processing was to print a message and `process.exit(1)`; the vendored
parser surfaces the violation as a thrown `Error` instead.)

Example: `minimist(["--enabled=true"], { boolean: ["enabled"] })` must throw.

## Code Style Requirements

- The parser must compile under `tsc --strict --target es2020 --module commonjs --esModuleInterop` with no errors.
- The new `minimist.ts` file must be standalone — it must not import any
  other file in the repo.
- `program.ts` and `session.ts` must use ES-module `import` syntax to obtain
  symbols from the new file (not `require()`); type-only references should
  use `import type`.
- The DEPS system is enforced via `DEPS.list` and checked by `npm run flint`.
  Files marked `"strict"` may only import what is explicitly listed.

## Out of scope

- Do not touch any other files under `packages/playwright-core/`.
- Do not introduce a new bundle directory — this parser is small enough to
  live as a single source file alongside the cli-client.
- Do not preserve compatibility with the dropped `minimist` features
  (aliases, defaults, etc.).

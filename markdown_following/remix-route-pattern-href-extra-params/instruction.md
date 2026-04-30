# RoutePattern href() Extra Params Type Error

## The Problem

Passing object literals with extra properties to `RoutePattern.href()` causes TypeScript
excess-property errors (TS2353).

```ts
let pattern = new RoutePattern("/posts/:id")
pattern.href({ id: "123", extra: "stuff" })
//                       ^^^^^ TS2353: 'extra' does not exist in type 'HrefParams<"/posts/:id">'
```

The `href()` method should silently ignore unrelated params — they don't affect URL
generation. Only missing required params should be an error.

## Affected Scenarios

Extra properties trigger TS2353 on object literals passed to href() in these cases:

- **Dynamic segments with extra params**: `pattern.href({ id: "123", extra: "stuff" })`
  where `pattern = new RoutePattern("/posts/:id")`
- **Multiple extra params**: `pattern.href({ id: "123", page: "2", sort: "desc" })`
- **Wildcard routes**: `pattern.href({ path: "docs/readme.md", mode: "fast" })` where
  `pattern = new RoutePattern("/files/*path")`
- **Repeated params**: Routes like `/:lang/users/:userId/:lang/posts/:postId` where the
  same param name appears multiple times

The existing test suite has tests for many of these patterns — check
`packages/route-pattern/src/lib/` for the type definitions and test files.

## Requirements

- Extra properties in object literals passed to `href()` must not cause TS2353 errors
- Required params must still be enforced (missing a required param is an error)
- Autocomplete for inferred params must continue to work
- Existing tests must continue to pass (run with `node --disable-warning=ExperimentalWarning --test`)
- The type-level change should be verified with `tsgo --noEmit -p tsconfig.json`

## Code Style Requirements

This project enforces formatting with **prettier** and linting with **eslint**. All code
must pass both checks:

- `prettier --check .` (or `pnpm format:check`) must return exit code 0
- `eslint . --max-warnings=0` (or `pnpm lint`) must return exit code 0

## Conventions

This repo follows conventions documented in `AGENTS.md` at the repository root. In
particular, note the rules for generics naming, import style, and formatting. The
`// prettier-ignore` comments on type definitions are intentional — preserve them.

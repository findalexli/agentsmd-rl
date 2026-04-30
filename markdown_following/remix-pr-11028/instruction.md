# Task: Rename match metadata property to `paramsMeta`

## Overview

In the `@remix-run/route-pattern` package, the `RoutePattern.match()` method and `Matcher.match()` method return match result objects. These results contain metadata about matched parameters (variables like `:id` and wildcards like `*path`) in the hostname and pathname.

This per-parameter metadata is analogous to `RegExp` groups and indices — each entry captures a matched parameter's name, type, value, and position within the URL. Consumers of this library need to access this metadata via a property called `paramsMeta`.

## Problem

The `paramsMeta` property does not exist on match result objects. Accessing `result.paramsMeta` returns `undefined`.

The metadata is present in the match result but is not reachable under the name `paramsMeta`. This affects:

1. **`RoutePattern.match()`** — the return type `RoutePatternMatch` and the `match()` method's return value
2. **`Matcher.match()`** (and `TrieMatcher.matchAll()`) — the `Match` type extends `RoutePatternMatch`, and the `TrieMatcher` implementation constructs match results
3. **`compare()` from `@remix-run/route-pattern/specificity`** — internally accesses this metadata on match objects to perform comparison
4. **Test assertions** — existing tests that directly access metadata on match results reference it by its current name

## What `paramsMeta` Should Look Like

The `paramsMeta` property should have this shape on match results:

```ts
paramsMeta: {
  hostname: PartPatternMatch   // array of matched hostname params
  pathname: PartPatternMatch   // array of matched pathname params
}
```

Each entry in the `PartPatternMatch` array is an object with fields like `name`, `type` (`:` for variables, `*` for wildcards), `value`, `begin`, and `end`.

Include a JSDoc comment on the property describing it as: "Rich information about matched params (variables and wildcards) in the hostname and pathname, analogous to RegExp groups/indices."

## Scope

The change is confined to `packages/route-pattern/`. The files that define or reference this metadata include:

- Type definition and `match()` return value (route-pattern module)
- `compare()` function internals (specificity module)
- TrieMatcher implementation returning match results
- Test files with assertions that access the metadata directly

Update all of these consistently so that the metadata is accessible as `paramsMeta` everywhere.

## Validation

After your changes, the following should work:

```ts
import { RoutePattern } from "@remix-run/route-pattern"
const pattern = new RoutePattern("/users/:id")
const result = pattern.match("https://example.com/users/123")
console.log(result.paramsMeta.pathname[0].name)  // "id"
console.log(result.paramsMeta.pathname[0].value) // "123"
```

And for the matcher:

```ts
import { TrieMatcher, RoutePattern } from "@remix-run/route-pattern"
const m = new TrieMatcher()
m.add(new RoutePattern("/users/:id"), "data")
const r = m.match("https://example.com/users/123")
console.log(r.paramsMeta.pathname[0].name)  // "id"
```

And the `compare()` function should work with match objects that carry `paramsMeta`:

```ts
import { compare } from "@remix-run/route-pattern/specificity"
// compare() reads paramsMeta internally
```

## Code Style Requirements

- Follow the conventions in the repository's `AGENTS.md` file at the repo root and in `packages/route-pattern/src/lib/route-pattern/AGENTS.md`
- Use `import type` for type-only imports, include `.ts` extensions
- Prefer `let` for local variables
- Use regular function declarations (not arrow functions) except for callbacks
- Format with Prettier (no semicolons, single quotes, printWidth 100)
- The existing test suite (`pnpm --filter @remix-run/route-pattern run test`) should continue to pass

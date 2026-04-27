# TrieMatcher: support pathname-only patterns

You are working in the `@remix-run/route-pattern` package at
`packages/route-pattern/`. The relevant module is the trie-based matcher.

## Symptom

`TrieMatcher` silently drops route patterns that have **no hostname** (i.e.,
pathname-only patterns). For example:

```ts
import { TrieMatcher } from './packages/route-pattern/src/lib/matchers/trie.ts'

let m = new TrieMatcher<null>()
m.add('users/:id', null)

m.match('https://example.com/users/123')   // returns undefined — wrong, expected a match
m.match('https://other.com/users/123')     // returns undefined — wrong, expected a match
```

These patterns should match **any** hostname (and any of the protocols the
pattern allows — both `http` and `https` when no protocol is specified). The
captured `params` should still come out correctly:

- `m.add('users', null)` → `m.match('https://example.com/users')` matches with `params == {}`
- `m.add('users/:id', null)` → `m.match('https://example.com/users/123')` matches with `params == { id: '123' }`
- `m.add('files/*path', null)` → `m.match('https://example.com/files/docs/readme.txt')` matches with `params == { path: 'docs/readme.txt' }`
- `m.add('api/users', null)` matches under `https://example.com/api/users`, `https://other.com/api/users`, and `http://localhost/api/users`.

## Additional requirements

In addition to making pathname-only patterns work, the following invariants
must hold for **all** matchers:

1. `TrieMatcher.prototype.match` must return **`null`** (not `undefined`) when
   no pattern matches. Today it can return `undefined`, which breaks callers
   that compare with `=== null`. The return type is already
   `Matcher.Match<...> | null`, so the runtime value must agree with that
   type.

2. Adding a pattern with an explicit hostname (e.g., `'://example.com/users'`)
   must continue to be scoped to that hostname — it must **not** start
   matching `https://other.com/users` as a side effect of fixing
   pathname-only support.

3. Existing behavior of patterns with explicit static hostnames, dynamic
   hostnames, variables, wildcards, and protocols must continue to work
   unchanged.

## Where to look

The matcher implementation and its existing tests live alongside each other
under `packages/route-pattern/src/lib/matchers/`. Treat the existing tests as
a regression suite — they must still pass.

## Code Style Requirements

This repository has an `AGENTS.md` at the repo root with mandatory
TypeScript conventions. Read it and follow it. Your changes will be checked
against (at minimum):

- **Imports**: prefer `import type { ... }` for type-only imports;
  relative imports should include the `.ts` extension consistent with the
  rest of the file.
- **Variables**: `let` for locals, `const` only at module scope, never
  `var`.
- **Classes**: native fields only — do not use TypeScript accessibility
  modifiers (`public`, `private`, `protected`); use `#private` for private
  members.
- **Formatting**: Prettier conventions (no semicolons, single quotes, 2-space
  indent, printWidth 100).

Your fix should be minimal and idiomatic for this file's existing style.

# Fix TrieMatcher route matching bugs

The `TrieMatcher` class in the route-pattern package is a prefix-trie-based
URL matcher. It implements the `Matcher` interface, allowing callers to
register route patterns and then match incoming URLs against them.

## Bug 1: Pathname-only patterns never match

A route pattern like `users/:id` specifies the pathname portion of a URL
without a hostname constraint. Such patterns are intended to match URLs with
**any** hostname (e.g., `https://example.com/users/123`,
`http://localhost/users/123`, `https://other.com/users/123`).

However, when you add a pathname-only pattern to the `TrieMatcher` and call
`match()` with a URL, no match is returned even when the URL's pathname
matches. The matcher silently returns no result.

This affects all pathname-only patterns: static segments (e.g., `users`),
variable segments (e.g., `users/:id`), wildcard segments (e.g.,
`files/*path`), and nested paths (e.g., `api/v1/users`).

## Bug 2: match() returns `undefined` instead of `null`

The `match()` method signature declares the return type as `Matcher.Match |
null`. Per the documented contract, callers expect `null` when no route
matches the given URL. But in certain no-match scenarios, `match()` returns
`undefined` instead of `null`. This violates the documented API contract and
can cause subtle bugs in callers that use strict equality checks (`=== null`).

## Where to look

The trie implementation lives in `packages/route-pattern/src/lib/matchers/`.
The `TrieMatcher` class delegates insertion and search to an internal `Trie`
class in the same file. Route patterns are decomposed into variants by a
`variants()` function, and each variant is inserted into a multi-level trie
structure keyed by protocol, hostname, port, and pathname segments.

## Expected behavior

After the fix, the following patterns should all match successfully:

| Pattern added | URL matched | Expected params |
|---|---|---|
| `users/:id` | `https://example.com/users/123` | `{ id: '123' }` |
| `api/v1/users/:id` | `https://other.com/api/v1/users/42` | `{ id: '42' }` |
| `files/*path` | `http://localhost/files/docs/readme.txt` | `{ path: 'docs/readme.txt' }` |

Additionally, `match()` must return `null` (not `undefined`) when a
hostname-specific pattern like `://example.com/users` is tested against
`https://other.com/users`.

## Code Style Requirements

The project uses Prettier with the following settings: `printWidth: 100`, no
semicolons, single quotes, spaces not tabs. TypeScript strict mode is
enabled. Import type-only types with `import type` (separate from value
imports), use `.ts` extensions in import paths, prefer `let` for locals,
`const` only at module scope, and avoid `var`. Class members use native
fields without TypeScript accessibility modifiers. Tests must not use loops
or conditionals within `describe()` blocks.

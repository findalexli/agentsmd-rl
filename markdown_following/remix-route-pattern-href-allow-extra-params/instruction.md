# Allow extra params in `RoutePattern.href` types

You're working in the `@remix-run/route-pattern` package of the
`remix-run/remix` monorepo, checked out at the parent of merge commit
`d96a99e1fa649f2a542a455d4f687c04853a1bd4`. The repo lives at
`/workspace/remix`.

## The bug

The `href()` method on `RoutePattern` is **typed too strictly**. At runtime
it already discards keys that the route pattern doesn't reference, but the
type definition rejects them via TypeScript's excess-property check.

For example, given:

```ts
let pattern = new RoutePattern("/posts/:id")
pattern.href({ id: 1, extra: "stuff" })
//                     ^^^^^
// 'extra' does not exist in type 'HrefParams<"/posts/:id">'
```

`tsgo --noEmit` (the package's typecheck script) reports an error on
`extra`, even though the call works fine at runtime and producing
`'/posts/1'` is the correct, intended behavior.

## What "fixed" means

After your changes, all of the following call shapes must **typecheck without
error**:

- `pattern.href({ id: '123', page: '2', sort: 'desc' })` — extra string keys
- `pattern.href({ id: 1, extra: 'stuff' })` — extra keys with a numeric required param
- `pattern2.href({ path: 'docs', other: 'thing' })` (where `pattern2` is `new RoutePattern('/files/*path')`) — extra keys alongside a wildcard param
- `pattern3.href({ userId: 'me', postId: '7', irrelevant: true })` (where
  `pattern3` is `new RoutePattern('/users/:userId/posts/:postId')`) — extra
  keys of any value type

At the same time, **required params must remain required**: the existing
test suite uses `// @ts-expect-error` on calls like `pattern.href({})` and
`pattern.href({ extra: 'only' })` (where the route demands `:id`) to assert
those still fail typecheck. Your fix must not turn those expected errors
into *unused* `@ts-expect-error` suppressions — i.e., it must not silently
make declared params optional or untyped.

Likewise, the package's existing runtime tests (run with `pnpm --filter
@remix-run/route-pattern run test`) must continue to pass. The fix is a
type-level change only.

## Where to look

The relevant types are exported from `packages/route-pattern/src/lib/types/`.
`HrefArgs<...>` and `HrefParams<...>` are the two types involved in typing
the `RoutePattern#href` method's argument list.

## How the verifier checks your work

1. `pnpm --filter @remix-run/route-pattern run typecheck` (no fixture) must
   succeed.
2. `pnpm --filter @remix-run/route-pattern run test` (the package's
   `node --test` suite) must succeed.
3. A type-only fixture is injected at
   `packages/route-pattern/src/lib/types/_href_type_fixture.ts` exercising
   the four call shapes listed above (plus `// @ts-expect-error` guards on
   missing-required-param calls). `pnpm ... typecheck` on the package +
   that fixture must succeed.

## Code Style Requirements

Follow the conventions in `AGENTS.md` at the repo root. Notably:

- Use `import type { ... }` for type-only imports; include the `.ts`
  extension on relative imports.
- Use **descriptive, lowercase** generic type-parameter names (e.g.
  `source`, `pattern`) rather than single uppercase letters like `T`. This
  is enforced repo-wide for new and modified generics.
- Prefer `let` for locals; reserve `const` for module-scope bindings.
- Strict TypeScript (`strict: true`, `verbatimModuleSyntax: true`) is on —
  no `any` workarounds.

You don't need to add or update a change file under
`packages/route-pattern/.changes/` — the harness doesn't grade that — but
following the repo's other conventions (per `AGENTS.md`) is part of doing
the task well.

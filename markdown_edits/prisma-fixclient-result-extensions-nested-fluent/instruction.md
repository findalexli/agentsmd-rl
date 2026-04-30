# Fix result extensions not applied for nested and fluent relations

## Problem

Prisma Client result extensions (computed fields registered via `$extends({ result: { ... } })`) are not applied correctly when data is accessed through nested relations or fluent API calls.

For example, if you register a computed `postLabel` field on `Post` via `$extends`, it works when querying posts directly:
```ts
const post = await xprisma.post.findFirst()
post.postLabel // works
```

But it does NOT work when accessing posts through a relation or fluent call:
```ts
// Nested include — computed field missing
const user = await xprisma.user.findFirst({ include: { posts: true } })
user.posts[0].postLabel // undefined — should have the computed value

// Fluent API — computed field missing
const posts = await xprisma.user.findUniqueOrThrow({ where: { email } }).posts()
posts[0].postLabel // undefined — should have the computed value
```

The root cause is in `packages/client/src/runtime/getPrismaClient.ts`. When applying result extensions, the code always uses the root request's model and args context. But for fluent relation calls, the runtime's `dataPath` unpacking has already narrowed the result to the nested relation object. The extension application needs to resolve the correct nested model/args context from the `dataPath` before applying extensions.

## Expected Behavior

Result extensions should be applied correctly regardless of how the data is accessed — direct queries, nested `include`/`select`, and fluent API relation calls should all have computed fields present.

The fix requires:
1. A new helper that resolves the effective extension context (model name + args) from the query's `dataPath`, interpreting it as `select|include` / relation-field pairs
2. Wiring that helper into `getPrismaClient.ts` so `applyAllResultExtensions` receives the resolved nested context instead of always using the root context

An important edge case: relation fields may themselves be named `select` or `include`. The resolver must not confuse these with selector keywords — it should walk the `dataPath` as structured pairs, not strip segments by string value.

After fixing the code, update `AGENTS.md` to document what you learned about `dataPath` construction in the fluent API, how extension context resolution should interpret it, and any testing implications for runtime changes affecting functional tests.

## Files to Look At

- `packages/client/src/runtime/getPrismaClient.ts` — where result extensions are applied after query execution
- `packages/client/src/runtime/core/extensions/` — extension application logic
- `packages/client/src/runtime/core/model/applyFluent.ts` — how fluent API builds the `dataPath`
- `packages/client/src/runtime/RequestHandler.ts` — how `dataPath` is currently unpacked
- `AGENTS.md` — agent knowledge base (should be updated with new learnings)

# Result extensions are not applied to nested and fluent relation queries

## Problem

When using Prisma Client result extensions with fluent API calls or nested includes, computed fields are silently missing from the results. For example, if you define a `postLabel` computed field via `$extends` on the `post` model, it works fine on direct `post.findMany()` calls, but is absent when accessed through fluent relations like `user.findUniqueOrThrow({ where: { email } }).posts()` or nested includes like `user.findFirst({ include: { posts: true } })`.

The root cause is in `packages/client/src/runtime/getPrismaClient.ts`: after a query executes, `applyAllResultExtensions` is called with the root model name and root args. But for fluent relation calls, the runtime uses `dataPath` to unpack the nested result first — so by the time extensions are applied, the payload is already the nested relation data (e.g., an array of posts), yet the extension code still walks it as if it were the root model (e.g., User). This means nested computed fields never fire.

## Expected Behavior

Result extensions should apply correctly regardless of how the data is queried:
- `user.findFirst({ include: { posts: true } })` → posts should have computed fields
- `user.findUniqueOrThrow({ where: ... }).posts()` → posts should have computed fields
- Multi-hop fluent chains should work too

The fix should resolve the effective model name and nested args from the `dataPath` before passing them to `applyAllResultExtensions`. The `dataPath` is structured as alternating selector/field pairs (`['select', 'posts']` or `['include', 'posts', 'select', 'author']`), and each field name corresponds to a relation on the current model in the runtime data model.

Be careful: relation fields can be literally named `select` or `include` — don't strip segments by matching raw string values.

After fixing the code, update `AGENTS.md` to document this dataPath behavior for future contributors. The architecture section should explain how `dataPath` is structured and interpreted for extension context resolution. Also note the relationship between functional test `.generated` clients and the runtime bundle.

## Files to Look At

- `packages/client/src/runtime/getPrismaClient.ts` — where `applyAllResultExtensions` is called with the wrong context
- `packages/client/src/runtime/core/extensions/` — extension application logic lives here
- `AGENTS.md` — agent knowledge base; update the Client architecture and Testing patterns sections

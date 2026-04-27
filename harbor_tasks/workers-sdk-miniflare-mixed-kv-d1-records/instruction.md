# Miniflare: mixed `kvNamespaces` / `d1Databases` records

You are working in the `cloudflare/workers-sdk` monorepo at
`/workspace/workers-sdk`. The Miniflare package lives at
`packages/miniflare/`.

## What's broken

Miniflare's public configuration accepts two shapes for KV and D1 bindings
inside a single record:

- a **string** value (the local namespace / database name), e.g.
  `LOCAL_NS: "local-ns"`
- an **object** value with at least an `id` field, e.g.
  `REMOTE_NS: { id: "remote-ns" }`

A user must be allowed to **mix both shapes inside the same record**, the
same way `r2Buckets` already supports. Today, that mixed shape is rejected
during construction.

Constructing a Miniflare like this:

```ts
new Miniflare({
    modules: true,
    script: "",
    kvNamespaces: {
        LOCAL_NS: "local-ns",
        REMOTE_NS: { id: "remote-ns" },
    },
});
```

throws a Zod validation error like:

```
Unexpected options passed to `new Miniflare()` constructor:
{
  ...,
  kvNamespaces: {
    LOCAL_NS: 'local-ns',
           ^1 Expected object, received string *or*
    REMOTE_NS: { id: 'remote-ns' },
            ^1 Expected string, received object
  },
}
```

The exact same problem applies to `d1Databases`. The `r2Buckets` schema in
the same codebase already accepts a mixed record and is the model to follow.

## Expected behaviour after the fix

All of the following constructions must succeed (no exception thrown by
`new Miniflare(...)`):

```ts
// kvNamespaces - mixed
new Miniflare({ modules: true, script: "", kvNamespaces: {
    LOCAL_NS: "local-ns",
    REMOTE_NS: { id: "remote-ns" },
}});

// d1Databases - mixed
new Miniflare({ modules: true, script: "", d1Databases: {
    LOCAL_DB: "local-db",
    REMOTE_DB: { id: "remote-db" },
}});
```

The pre-existing forms must keep validating:

- All-string record: `{ NS1: "ns-one", NS2: "ns-two" }`
- All-object record: `{ NS1: { id: "id-one" }, NS2: { id: "id-two" } }`
- String-array form: `["A", "B", "C"]`

And these invalid inputs must still be rejected:

- Numeric value in a record (e.g. `{ BAD: 42 }`)
- Object value missing the `id` field (e.g. `{ BAD: { notAnId: "x" } }`)

## Notes

- The runtime helper that reads these records already handles both value
  shapes correctly today — only the schema-level validation is too strict.
- Look at the `r2Buckets` schema for the pattern that already works.
- After editing the schema source files, you must rebuild the miniflare
  package so that `packages/miniflare/dist/src/index.js` reflects your
  changes. The repo uses pnpm:

    ```
    pnpm --filter miniflare run build
    ```

- This change is a user-facing bug fix to a published package. Add a
  patch-level changeset under `.changeset/` per the repo's rules
  (see `AGENTS.md` and `.changeset/README.md`).

## Code Style Requirements

Match the repo's existing TypeScript style:

- Tabs (not spaces), double quotes, semicolons, trailing commas (es5)
- No `any` type, no non-null assertions (`!`)
- Use `pnpm` for any package commands — never `npm` or `yarn`

## Files of interest

- `packages/miniflare/src/plugins/r2/index.ts` — has the model schema
- `packages/miniflare/test/index.spec.ts` — has the existing
  `accepts mixed r2Buckets record` test as a pattern
- `AGENTS.md` (root) and `packages/miniflare/AGENTS.md` — repo conventions

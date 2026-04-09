# Custom ID fields nested in tabs/groups are ignored by MongoDB adapter

## Problem

When a custom `id` field is defined inside a tab or unnamed group field, the MongoDB adapter ignores it. Instead of using the custom ID, MongoDB falls back to auto-generating ObjectIDs.

For example, a collection like this doesn't work correctly:

```typescript
{
  slug: 'my-collection',
  fields: [
    {
      type: 'tabs',
      tabs: [
        {
          label: 'Main',
          fields: [
            { name: 'id', type: 'number' },
            { name: 'title', type: 'text' },
          ],
        },
      ],
    },
  ],
}
```

Creating a document with `id: 12345` results in the document getting an auto-generated ObjectID instead of using `12345` as its ID.

Additionally, even if the schema issue is fixed, documents returned from the database have their custom ID field stripped out during the afterRead hook processing — because the ID field is marked as hidden and the hook removes all hidden fields indiscriminately.

## Expected Behavior

- The MongoDB schema builder should find and respect custom `id` fields regardless of how deeply they're nested within tabs, groups, or other container fields.
- The afterRead hook should preserve top-level custom ID fields even when they're marked as hidden, since these need to remain accessible.

## Files to Look At

- `packages/db-mongodb/src/models/buildSchema.ts` — Builds Mongoose schemas; currently only searches top-level fields for a custom `id`
- `packages/db-mongodb/src/models/buildCollectionSchema.ts` — Calls `buildSchema` for each collection
- `packages/payload/src/fields/hooks/afterRead/promise.ts` — Processes fields after reading from DB; removes hidden fields
- `packages/payload/src/fields/hooks/afterRead/traverseFields.ts` — Traverses field tree for afterRead processing
- `packages/payload/src/fields/hooks/afterRead/index.ts` — Entry point for afterRead hook

After fixing the code, update the project's `CLAUDE.md` to document best practices for writing tests — specifically around test self-containment and cleanup. The existing Testing section has commands but no guidance on how tests should be structured.

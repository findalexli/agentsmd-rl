# Task: Fix SDK trash parameter not passed to REST requests

## Symptom

When using the Payload REST SDK (`@payloadcms/sdk`), the `trash` option documented for `find`, `findVersions`, `findVersionByID`, `count`, `update`, and `delete` operations has no effect. Calls like:

```typescript
sdk.find({ collection: 'posts', trash: true })
```

produce HTTP requests that do not include the `trash` query parameter, even though the REST API and Local API both support it.

## Root Cause

The utility function that serializes SDK operation arguments into a REST API query string does not handle the `trash` boolean. It serializes `draft`, `depth`, `pagination`, and other options — but `trash` is silently dropped.

## Relevant Files

- `packages/sdk/src/utilities/buildSearchParams.ts` — builds the query string from operation args
- `packages/sdk/src/collections/count.ts` — `CountOptions` type
- `packages/sdk/src/collections/findByID.ts` — `FindByIDOptions` type
- `packages/sdk/src/collections/update.ts` — `UpdateBaseOptions` type
- `packages/sdk/src/collections/delete.ts` — `DeleteBaseOptions` type

## Expected Behavior

The `buildSearchParams` utility must serialize the `trash` boolean into the query string, analogous to how it already handles `draft`, `depth`, `limit`, and other options. When `trash: true` is passed, the resulting query string must include `trash=true`; when `trash: false`, it must include `trash=false`; and when `trash` is not provided, no `trash` parameter should appear. The `OperationArgs` type should be extended so that `trash` is recognized as a valid boolean option.

# Fix VectorDB Metadata Race Condition

## Problem

The VectorDB collection creation endpoint has a race condition when handling concurrent requests that initialize metadata. When two parallel requests both check if the metadata collection exists and find it doesn't, they both attempt to create it, causing one to fail with a `DuplicateException`.

## Location

The issue is in `src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php` in the `action` method.

## Symptoms

- Flaky tests during parallel test runs involving CSV export migration
- Intermittent `DuplicateException` errors when creating VectorDB collections
- Race condition between checking `exists()` and calling `create()` on the metadata collection

## Expected Behavior

The metadata bootstrap should be idempotent under concurrency. When multiple requests race to create the metadata:

1. Both requests check if metadata exists and get `false`
2. Both attempt to create the metadata
3. One succeeds, the other gets a `DuplicateException`
4. The duplicate exception is benign - the metadata is now present
5. Both requests can proceed to create their actual collections

The fix should only affect the one-time metadata bootstrap, not hide duplicate errors for actual user collection creation.

## Constraints

- Keep duplicate handling scoped only to the one-time metadata bootstrap
- Do NOT suppress duplicate errors for actual collection creation in `createCollection()`
- The exception being caught is `Appwrite\Extend\Exception\DuplicateException`
- Remove the outdated comment about "passing null in creates only creates the metadata collection"

## Module Conventions

Refer to the module structure and HTTP endpoint conventions documented in the repository's AGENTS.md files. This file follows the standard Action pattern with HTTP endpoints under `Http/VectorsDB/Collections/`.

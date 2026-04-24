# Fix VectorsDB Metadata Bootstrap Race Condition

## Problem

When multiple requests concurrently create the first collection in a VectorsDB database, a race condition causes intermittent failures. The current implementation checks if database metadata exists before attempting to create it, but between the check and the creation, another concurrent request may have already created the metadata. This causes one of the requests to fail with an error.

The flaky failures happen because the existence check and creation are not atomic.

## Task

Fix the race condition in the metadata bootstrapping code located at:

`src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php`

The fix must:

1. **Include explanatory comments** (exact strings required by the tests):
   - `Bootstrap the database metadata without a separate existence`
   - `avoid races when multiple first collections are created`

2. **Remove the check-then-create pattern**: Do NOT check if metadata exists before calling create. This atomicity problem is the root cause of the race condition.

3. **Use a retry loop**: Implement a retry mechanism that attempts creation without a pre-check. The loop must call `$dbForDatabases->create()` inside it and use a `break` statement on success.

4. **Handle exceptions appropriately**:
   - When `DuplicateException` is caught, the metadata was already created by another request — handle this case appropriately (the exact handling is your design decision)
   - When other exceptions occur, check if metadata now exists (using `$dbForDatabases->exists()`) and decide whether to retry or propagate the error
   - Include a delay between retry attempts using `usleep()`

5. **Enforce a maximum attempt limit**: Track attempts and throw an exception if the limit is exceeded rather than retrying indefinitely.

6. The modified file must pass PHP syntax checks (`php -l`), linting (`composer lint`), and static analysis (`composer analyze`).

## Success Criteria

Concurrent metadata bootstrapping should succeed without flaky failures. The implementation must include the exact comment strings and eliminate the race condition by removing the check-then-create pattern.

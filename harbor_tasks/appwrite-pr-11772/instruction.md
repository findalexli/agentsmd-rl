# Fix VectorsDB Metadata Bootstrap Race Condition

There's a flaky failure occurring when creating the first collection in a VectorsDB database under concurrent load. Two concurrent requests can race through the database initialization, causing one to fail.

## Problem

The current implementation in `src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php` uses a non-atomic pattern:

1. Check if metadata exists (`exists()` call)
2. If not, create it (`create()` call)

Under concurrent CI load, two requests can both pass the existence check, then both try to create, causing one to fail with an error from the Swoole PDO proxy.

## Requirements

Fix the race condition by:

1. **Remove the separate existence check** - Don't check if metadata exists before trying to create

2. **Implement a retry loop** - Wrap the `create()` call in a loop that attempts up to 5 times

3. **Handle DuplicateException** - If `create()` throws a `DuplicateException`, the metadata was already created by another request, so break out of the loop

4. **Handle other exceptions** - For other `Throwable` errors:
   - Check if the metadata now exists (another request may have succeeded)
   - If it exists, break out of the loop
   - If it doesn't exist and we haven't exhausted retries, sleep for 100ms and retry
   - After 5 failed attempts, rethrow the exception

5. **Add explanatory comments** - Document why this approach is needed to handle concurrent collection creation

## Key File

`src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php` - The `action()` method contains the logic that needs to be fixed (around line 130).

## Notes

- The fix makes the metadata bootstrap idempotent even when the adapter surfaces race conditions as non-DuplicateException errors
- This is a common pattern for handling concurrent initialization in distributed systems
- Look for the `Database::METADATA` constant usage to find the relevant code section

# Fix VectorsDB Metadata Bootstrap Race Condition

## Problem

There's a flaky failure when creating the first collection in a VectorsDB database under concurrent load. The current code uses a non-atomic pattern: it first checks if metadata exists, then tries to create it. Two concurrent requests can both pass the existence check, then both try to create metadata, causing one to fail with errors from the Swoole PDO proxy.

## Location

The buggy pattern is in the database metadata bootstrap code in `src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php`.

## Requirements

Your fix must satisfy all of the following:

1. **Remove the race-prone existence check** - The code currently pre-checks if `Database::METADATA` exists before calling `create()`. This check-and-create pattern must be eliminated entirely.

2. **Add explanatory comments** - The code must include these exact comment lines:
   - `Bootstrap the database metadata without a separate existence`
   - `avoid races when multiple first collections are created`

3. **Implement retry logic** - After the comments, the code must use a retry mechanism with:
   - A `for` loop using the variable name `$attempt`, starting at `0`, looping while `$attempt < 5`, with increment `$attempt++`
   - Inside the loop, a `try` block containing `$dbForDatabases->create()` followed by `break`
   - A `catch (DuplicateException)` handler that executes `break`
   - A `catch (\Throwable $e)` handler that:
     - Checks if `$dbForDatabases->exists(null, Database::METADATA)` is true and breaks if so
     - Checks if `$attempt === 4` and rethrows the exception if so
     - Calls `\usleep(100_000)` before the next retry

## Success Criteria

After your changes, the metadata bootstrap should handle concurrent initialization gracefully. The code must no longer pre-check existence before attempting creation. The implementation must include the exact variable names, string literals, and control flow described above.

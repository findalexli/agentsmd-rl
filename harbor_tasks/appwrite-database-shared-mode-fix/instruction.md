# Fix Shared-Mode Database Configuration Issues

## Problem

The Appwrite database layer has several issues when running in shared-mode CI configuration:

### Issue 1: Invalid (int) Cast on MongoDB UUID Sequences
In `app/init/resources/request.php` and `app/init/worker/message.php`, the `setTenant()` method is called with `(int) $project->getSequence()` or `(int) $projectDocument->getSequence()`. This truncates MongoDB UUID sequences, causing tenant ID mismatches.

**Fix**: Remove the `(int)` cast so the raw sequence value is passed to `setTenant()`.

### Issue 2: Empty String Matching in Shared Tables
The `_APP_DATABASE_SHARED_TABLES` environment variable is parsed with just `explode(',', ...)`, which creates an array with an empty string when the env var is unset. This causes incorrect matches in `in_array()` checks.

**Fix**: Wrap the `explode()` calls with `array_filter()` to remove empty strings before checking.

### Issue 3: Cross-Engine Tenant Type Mismatches for Separate Pools
When documentsdb or vectorsdb uses a different database engine than the main project database, the shared tables configuration doesn't account for this. This leads to cross-engine tenant type mismatches.

**Fix**: Add adapter-based separate pool detection in both `request.php` and `worker/message.php`. When the database host differs from the main DSN host, check the type-specific shared tables config (DOCUMENTSDB or VECTORSDB) and fall back to dedicated mode if not configured.

### Issue 4: Garbage DSN Construction and Missing Pool Validation
In `src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php`:
- The shared tables arrays aren't filtered, allowing empty strings
- Pool filtering happens even when shared tables env vars are unset
- No error is thrown when no pool is available after filtering

**Fix**:
1. Add `array_filter()` on `explode()` calls for `_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES`, `_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES_V1`, `_APP_DATABASE_VECTORSDB_SHARED_TABLES`, and `_APP_DATABASE_VECTORSDB_SHARED_TABLES_V1`
2. Add `!empty($databaseSharedTables)` check before pool filtering
3. Add explicit `if (empty($databases))` check that throws `Exception(Exception::GENERAL_SERVER_ERROR, "No {$databasetype} database pool available for the current shared-tables mode")`

## Files to Modify

1. `app/init/resources/request.php` - Fix tenant cast, add array_filter, add separate pool detection
2. `app/init/worker/message.php` - Fix tenant cast, add array_filter, add separate pool detection
3. `src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php` - Fix shared tables filtering and add pool availability check

## Notes

- This is a PHP codebase using the Utopia framework
- The changes should follow PSR-12 formatting conventions
- Ensure the code validates with `php -l` syntax checks

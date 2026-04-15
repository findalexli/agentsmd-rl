# Fix Shared-Mode Database Configuration Issues

The Appwrite database layer has several issues when running in shared-mode CI configuration. The following symptoms have been observed:

## Issue 1: Tenant ID Mismatch from Type Truncation

**Symptom:** When using MongoDB with UUID-based project sequences, tenant data is being associated with incorrect projects, causing cross-tenant data leaks or missing data.

**Observed in:** `app/init/resources/request.php` and `app/init/worker/message.php`

**Required behavior:**
- The code passes the raw sequence value to `setTenant()` without any type casting that would truncate the value
- The method call pattern must be `->setTenant($project->getSequence())` or `->setTenant($projectDocument->getSequence())` exactly

## Issue 2: Empty String Matching in Environment Variable Parsing

**Symptom:** When `_APP_DATABASE_SHARED_TABLES` is unset, the code incorrectly matches empty strings in `in_array()` checks, causing shared tables to be enabled when they should not be.

**Observed in:** `app/init/resources/request.php` and `app/init/worker/message.php`

**Required behavior:**
- The code must filter out empty strings after exploding the comma-separated environment variable `_APP_DATABASE_SHARED_TABLES`
- The resulting code must contain the exact pattern: `array_filter(\explode(',', System::getEnv('_APP_DATABASE_SHARED_TABLES', '')))`

## Issue 3: Cross-Engine Tenant Type Mismatches for Separate Pools

**Symptom:** When documentsdb or vectorsdb uses a different database host than the main project database, tenant type mismatches occur because the shared tables configuration doesn't account for separate pools.

**Observed in:** `app/init/resources/request.php` and `app/init/worker/message.php`

**Required behavior:**
- The code must check if the database host differs from the main DSN host using a pattern like `$databaseHost !== $dsn->getHost()`
- For separate pools, the code must look up type-specific shared tables configurations:
  - For DOCUMENTSDB: `DOCUMENTSDB => \array_filter(\explode(',', System::getEnv('_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES', '')))`
  - For VECTORSDB: `VECTORSDB => \array_filter(\explode(',', System::getEnv('_APP_DATABASE_VECTORSDB_SHARED_TABLES', '')))`
- If the separate pool is not configured for shared tables, the code must use dedicated mode (setSharedTables(false), setTenant(null), setNamespace with underscore prefix)

## Issue 4: Missing Pool Validation and Empty String Contamination

**Symptom:** In database creation, when shared tables arrays contain empty strings or when no pool is available after filtering, the code silently proceeds instead of failing fast with a clear error.

**Observed in:** `src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php`

**Required behavior:**
- All `explode()` calls for the following environment variables must be wrapped with `array_filter()`:
  - `_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES`
  - `_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES_V1`
  - `_APP_DATABASE_VECTORSDB_SHARED_TABLES`
  - `_APP_DATABASE_VECTORSDB_SHARED_TABLES_V1`
- Before filtering pools, the code must check that the shared tables variable is not empty: `if (!empty($dsn) && !empty($databaseSharedTables))`
- If no database pools remain after filtering, the code must throw an exception with `Exception::GENERAL_SERVER_ERROR` and the exact message: `"No {$databasetype} database pool available for the current shared-tables mode"`
- The code must explicitly check `if (empty($databases))` before calling `array_rand()`

## Files to Modify

1. `app/init/resources/request.php`
2. `app/init/worker/message.php`
3. `src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php`

## Verification Requirements

After modification, the code must:
- Pass `php -l` syntax validation
- Pass `composer lint` checks
- Pass `phpstan` static analysis

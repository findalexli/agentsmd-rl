# Fix Shared-Mode Database Configuration Issues

The Appwrite database layer has several bugs when running in shared-mode CI configuration. The following issues have been observed:

## Issue 1: Tenant ID Mismatch from Type Truncation

**Symptom:** When using MongoDB with UUID-based project sequences, tenant data is being associated with incorrect projects, causing cross-tenant data leaks or missing data. The tenant ID is being truncated.

**Root cause:** The code passes a type-cast sequence value to `setTenant()`, which truncates UUID strings.

**Required behavior:**
- The code must pass the raw sequence value to `setTenant()` without any type casting that would truncate the value
- UUID-based sequences like "550e8400e29b41d4a716446655440000" must be preserved intact

## Issue 2: Empty String Matching in Environment Variable Parsing

**Symptom:** When `_APP_DATABASE_SHARED_TABLES` is unset or empty, the code incorrectly matches empty strings in `in_array()` checks, causing shared tables to be enabled when they should not be.

**Root cause:** The `explode()` function on an empty string returns `[""]`, and `in_array("", [""])` returns true.

**Required behavior:**
- Empty strings resulting from parsing unset/empty environment variables must be filtered out before `in_array()` checks
- The `_APP_DATABASE_SHARED_TABLES` environment variable parsing must not allow empty string matches

## Issue 3: Cross-Engine Tenant Type Mismatches for Separate Pools

**Symptom:** When documentsdb or vectorsdb uses a different database host than the main project database, tenant type mismatches occur because the shared tables configuration doesn't account for separate pools.

**Root cause:** The code uses the same shared tables configuration for all database types, even when they have separate connection pools with different hosts.

**Required behavior:**
- The code must detect when a database type (documentsdb, vectorsdb) uses a separate pool by comparing the configured database host with the main DSN host
- For separate pools, the code must look up type-specific shared tables configurations (e.g., `_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES`, `_APP_DATABASE_VECTORSDB_SHARED_TABLES`)
- If the separate pool is not configured for shared tables, the code must use dedicated mode with:
  - `setSharedTables(false)`
  - `setTenant(null)`
  - A namespace with underscore prefix

## Issue 4: Missing Pool Validation and Empty String Contamination

**Symptom:** In database creation, when shared tables arrays contain empty strings or when no pool is available after filtering, the code silently proceeds with an empty selection instead of failing fast with a clear error.

**Root cause:** The code doesn't validate that pools remain after filtering, and empty strings from parsing contaminate the shared tables arrays.

**Required behavior:**
- All environment variables used for shared tables configuration must have empty strings filtered out:
  - `_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES`
  - `_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES_V1`
  - `_APP_DATABASE_VECTORSDB_SHARED_TABLES`
  - `_APP_DATABASE_VECTORSDB_SHARED_TABLES_V1`
- Before filtering pools, the code must check that the shared tables variable is not empty
- If no database pools remain after filtering, the code must throw an exception with code `Exception::GENERAL_SERVER_ERROR` and a descriptive error message indicating no pool is available for the current shared-tables mode
- The code must explicitly check if the pools array is empty before attempting to select a random pool

## Files to Modify

1. `app/init/resources/request.php`
2. `app/init/worker/message.php`
3. `src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php`

## Verification Requirements

After modification, the code must:
- Pass `php -l` syntax validation
- Pass `composer lint` checks
- Pass `phpstan` static analysis

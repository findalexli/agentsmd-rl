# Fix VectorsDB Metadata Bootstrap Race Condition

## Problem

When multiple requests concurrently create the first collection in a VectorsDB database, a race condition causes intermittent failures. The current implementation checks if database metadata exists before attempting to create it, but between the check and the creation, another concurrent request may have already created the metadata. This causes one of the requests to fail unexpectedly.

This manifests as flaky failures during concurrent collection creation operations.

## Task

Fix the race condition in the metadata bootstrapping code. The solution should:

1. **Include explanatory comments** with these exact phrases:
   - `Bootstrap the database metadata without a separate existence`
   - `avoid races when multiple first collections are created`

2. **Handle concurrent metadata creation safely**:
   - Attempt to create metadata without checking existence first
   - If another request already created the metadata (detected via DuplicateException or by checking existence after a failure), stop retrying and continue normally
   - If creation fails for other reasons, retry with a small delay
   - After multiple failed attempts, propagate the error
   - Do NOT check for existence before attempting creation (this pattern causes the race condition)

3. The implementation should be resilient to concurrent access patterns common in high-traffic environments.

4. The modified file must pass PHP syntax checks (`php -l`), linting (`composer lint`), and static analysis (`composer analyze`).

## Success Criteria

After your changes, concurrent metadata bootstrapping should succeed without flaky failures. The implementation must include the exact comment strings specified above and eliminate the race condition by removing the check-then-create pattern.

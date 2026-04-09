# Add Per-Tenant Sharding Configuration to Compactor

## Problem

The compactor currently uses a global `shard_size` configuration that applies to all collections uniformly. We need to implement per-tenant sharding controls so that:

1. Only specific tenants can have sharding enabled
2. A tenant pattern system supports wildcards (e.g., `"*"` for all tenants)
3. The `CompactionJob` structure carries tenant information

## Files to Modify

### 1. `rust/worker/src/compactor/config.rs`
Add `sharding_enabled_tenant_patterns: Vec<String>` field to `CompactorConfig`. This should:
- Support `"*"` wildcard to enable sharding for all tenants
- Support exact tenant ID matches
- Default to empty (no sharding enabled)
- Update doc comments to reflect new behavior

### 2. `rust/worker/src/compactor/types.rs`
Add `tenant_id: String` field to the `CompactionJob` struct.

### 3. `rust/worker/src/compactor/scheduler.rs`
When creating `CompactionJob` instances, populate the `tenant_id` field from the collection record.

### 4. `rust/worker/src/compactor/scheduler_policy.rs`
When scheduling compaction jobs, include the `tenant_id` from the collection.

### 5. `rust/worker/src/compactor/compaction_manager.rs`
Make these changes:
1. Add `sharding_enabled_tenant_patterns: Vec<String>` to `CompactionManagerContext`
2. Implement `tenant_matches_patterns(tenant_id: &str, patterns: &[String]) -> bool` function that:
   - Returns `true` if patterns contain `"*"`
   - Returns `true` if any pattern matches the tenant_id exactly
   - Returns `false` for empty patterns or no match
3. Pass `tenant_id` through the compaction flow
4. In the `compact` method, determine `shard_size` by checking if tenant matches patterns
5. Update `rebuild_batch` to fetch collections from sysdb and extract tenant information

## Testing

The implementation should:
- Pass `cargo check` in `rust/worker`
- Correctly match tenants against patterns (wildcards and exact matches)
- Default to disabled sharding when no patterns are configured

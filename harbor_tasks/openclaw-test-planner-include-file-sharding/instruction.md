# Bug: Test planner over-shards single include-file CI batches

## Context

The test planner in `scripts/test-planner/` orchestrates parallel Vitest runs in CI. When running with multiple shards (e.g., `OPENCLAW_TEST_SHARDS=4`), it assigns small test units to specific shards to avoid passing invalid `--shard=x/N` arguments to Vitest when a unit has fewer files than shards.

The shard-assignment logic in `planner.mjs` (around the `buildTopLevelSingleShardAssignments` function) decides which test units are small enough to pin to a single shard. It does this by counting how many entry files a unit targets. Similarly, the plan formatter in `executor.mjs` (`formatPlanOutput`) and summary formatter in `planner.mjs` (`formatExecutionUnitSummary`) display the filter count for each unit.

## Bug

The filter-counting logic only checks for explicit CLI entry filters via `countExplicitEntryFilters(unit.args)` from `vitest-args.mjs`. However, many test units specify their file scope via `unit.includeFiles` arrays rather than CLI passthrough arguments. When a unit has `includeFiles: ["some-test.test.ts"]` but no explicit CLI file filters, the count comes back as `null`.

This causes two problems:

1. **Over-sharding**: Single-file include batches don't get assigned to one shard. Instead they go through the normal sharding path and receive `--shard=x/4` (or similar) arguments, which is invalid when the unit only covers one file.

2. **Incorrect plan output**: The plan summary shows `filters=all` for include-file batches instead of showing the actual file count, making the plan output misleading.

## Scope

The fix should touch `scripts/test-planner/executor.mjs` and `scripts/test-planner/planner.mjs`. Both files use `countExplicitEntryFilters(unit.args)` in several places where `unit.includeFiles` should also be considered as a fallback.

## Verification

Run the test planner tests:
```
pnpm test -- test/scripts/test-planner.test.ts test/scripts/test-parallel.test.ts
```

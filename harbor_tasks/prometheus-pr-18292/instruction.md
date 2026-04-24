# Fix Race Condition in TSDB Agent Series Creation

## Problem

The TSDB agent has a race condition: when multiple goroutines concurrently append samples for the same label set, both can observe the series as absent and both insert, producing duplicate in-memory series and duplicate WAL records. This causes data inconsistency and resource waste.

## Expected Behavior

Concurrent appends for the same label set must:

1. Produce exactly **one** series in memory
2. Produce exactly **one** series record in the WAL
3. Return the same canonical series reference to all concurrent callers
4. Clean up any refs created by losing concurrent goroutines (no leaks)

## Requirements

The `stripeSeries` type in `tsdb/agent/series.go` must provide an atomic "check-then-insert" operation that:

- Returns the canonical series for a label set (newly inserted or pre-existing)
- Returns a boolean indicating whether insertion occurred
- Cleans up loser refs when a concurrent insert wins
- Does not hold multiple stripe locks simultaneously (deadlock risk with GC)

The `getOrCreate` method in the agent package must be updated to support callers that already hold a series reference, allowing them to skip redundant lookups. The package must build cleanly.

## Verification

Run the agent tests to verify your fix:

```bash
cd /workspace/prometheus
go test -v -run 'TestConcurrentAppendSameLabels|TestStripeSeries_SetUnlessAlreadySet|TestSetUnlessAlreadySetConcurrentSameLabels|TestSetUnlessAlreadySetConcurrentGC' ./tsdb/agent/
go build ./tsdb/agent/
```

All four tests must pass and the package must compile.

## Constraints

- Follow the existing code style in the repository
- Ensure all comments start with a capital letter and end with a full stop
- Do not hold multiple stripe locks simultaneously
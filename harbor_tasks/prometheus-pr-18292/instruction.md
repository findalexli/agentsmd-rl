# Fix Race Condition in Agent Series Creation

## Problem

The Prometheus agent's `getOrCreate` method in the TSDB agent package has a race condition. When multiple goroutines concurrently append samples for the same label set, they can both observe the series as absent and both insert, producing:

1. **Duplicate in-memory series** for the same label set
2. **Duplicate WAL records** referencing different series refs

This leads to data inconsistency and unnecessary resource usage.

## Expected Behavior

Concurrent appends for the same label set should:

1. Produce exactly **one** series in memory
2. Produce exactly **one** series record in the WAL
3. All concurrent callers should receive the same canonical series reference
4. Losing refs from race losers should be cleaned up (not leak)

## Technical Requirements

### getOrCreate signature change

The `getOrCreate` method in `tsdb/agent/db.go` must be updated to accept a reference parameter. The new signature should be:

```go
getOrCreate(ref chunks.HeadSeriesRef, l labels.Labels) (*memSeries, error)
```

The first parameter (`ref`) allows callers that already have a valid series reference to skip the lookup entirely. When `ref` is zero, the method falls back to looking up the series by label hash.

### New method requirement

The `stripeSeries` type in `tsdb/agent/series.go` must implement a method that provides atomic "check-then-insert" behavior for series lookup and insertion. This prevents two goroutines from both inserting the same label set.

The method must:
- Return the canonical series for the label set (whether newly inserted or pre-existing)
- Return a boolean indicating whether insertion occurred
- Clean up any "losing" refs when a concurrent insertion wins
- Not hold multiple stripe locks simultaneously (to avoid deadlock with GC)

### Callers to update

After the signature change, update all callers of `getOrCreate` in:
- `tsdb/agent/db.go` (Append, AppendHistogram, AppendHistogramSTZeroSample, AppendSTZeroSample)
- `tsdb/agent/db_append_v2.go` (Append)

Each caller should pass the ref they already have (or 0 if unknown) as the first argument.

## Verification

Run the agent tests to verify your fix:

```bash
cd /workspace/prometheus
go test -v -run 'TestConcurrentAppendSameLabels|TestStripeSeries_SetUnlessAlreadySet|TestSetUnlessAlreadySetConcurrentSameLabels|TestSetUnlessAlreadySetConcurrentGC' ./tsdb/agent/
go build ./tsdb/agent/
```

All four tests must pass.

## Constraints

- Follow the existing code style in the repository
- Ensure all comments start with capital letter and end with full stop
- The fix should maintain or improve performance characteristics
- Do not hold multiple stripe locks simultaneously (deadlock risk with GC)
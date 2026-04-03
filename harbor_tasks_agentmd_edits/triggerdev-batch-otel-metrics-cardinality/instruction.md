# Fix high-cardinality OpenTelemetry metric attributes in batch queue

## Problem

The batch queue in `internal-packages/run-engine/src/batch-queue/index.ts` uses high-cardinality attributes in its OpenTelemetry metric recordings. Specifically, metric counters and histograms include attributes like `envId` (a UUID) and `itemCount` (an unbounded integer) which create an explosion of unique time series in the metrics backend.

This causes memory bloat, slow dashboard queries, increased costs, and potential data loss at scale — each unique combination of attribute values creates a new time series in backends like Axiom or Prometheus.

## Expected Behavior

All metric `.add()` and `.record()` calls in the batch queue should use **low-cardinality** attributes only:
- Use bounded enums (like environment type) instead of UUIDs
- Use booleans instead of unbounded integers
- Error codes are acceptable since they come from a finite set

Additionally, the `itemQueueTimeHistogram` currently records before the batch meta is available — it should be moved to after the meta lookup so it can use the correct low-cardinality attribute.

After fixing the code, add a Cursor rule (`.cursor/rules/`) documenting OpenTelemetry metric guidelines for the project so that future contributors avoid reintroducing high-cardinality attributes. The rule should cover what constitutes high vs low cardinality and apply to TypeScript files.

## Files to Look At

- `internal-packages/run-engine/src/batch-queue/index.ts` — the batch queue with metric recording calls
- `internal-packages/run-engine/src/batch-queue/types.ts` — type definitions including `BatchMeta` and `InitializeBatchOptions` which have an `environmentType` field
- `.cursor/rules/` — existing Cursor rules for the repo (add a new one for metrics guidelines)

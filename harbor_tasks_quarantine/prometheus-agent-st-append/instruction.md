# Fix Start Timestamp Persistence in Prometheus Agent Mode

## Problem

In Prometheus agent mode with the `--enable-feature=st-storage` flag enabled, start timestamps (ST) are not being correctly persisted to the Write-Ahead Log (WAL) when appending samples.

When `EnableSTStorage` is set to `true` and samples are appended via the `AppenderV2` interface with non-zero start timestamps, reading back the WAL records shows those start timestamp values as 0. Specifically, after appending samples and committing, decoding `record.SamplesV2` entries from the WAL yields `record.RefSample` structs whose `ST` field is always 0, regardless of the start timestamp values passed to the append call.

For example, if you create a test DB using `createTestAgentDB` with `EnableSTStorage = true`, obtain an appender via `AppenderV2`, and append samples with ST values like `[1000, 2000, 3000, 4000, 5000]`, then after `Commit()` and closing the DB, reading back the WAL segments and decoding `record.SamplesV2` records should yield `record.RefSample` entries with matching `ST` values. Currently, all `ST` values come back as 0.

## Context

- The `EnableSTStorage` option (controlled by the `--enable-feature=st-storage` CLI flag) enables writing start timestamps alongside samples in the WAL
- In the `tsdb/agent` package, the `AppenderV2` append interface receives a start timestamp parameter (`st`) when adding samples -- this value should flow through to `record.RefSample.ST` in the WAL records so it survives WAL replay
- The expected behavior is that when `EnableSTStorage` is enabled and samples are appended with a non-zero start timestamp, those exact ST values must be recoverable by reading the WAL, decoding `record.SamplesV2` records, and inspecting each `record.RefSample.ST` field

## What You Need to Do

1. Investigate the sample appending flow in the `tsdb/agent` package -- find where start timestamp values received during append are being dropped instead of persisted to `record.RefSample.ST`
2. Fix the issue so that start timestamps are included when sample records are written to the WAL
3. Ensure the fix works for varying ST values (e.g., `[1234, 2234, 3234, 4234, 5234]`) and different label sets (e.g., labels like `__name__=test_metric` or `__name__=test_varying`)

## How Verification Works

The tests verify ST persistence by writing temporary Go test files directly to the `tsdb/agent` package directory. These test files create a test agent DB via `createTestAgentDB`, append samples using `AppenderV2` with specific ST values (such as `[1000, 2000, 3000, 4000, 5000]`), commit the appender, close the DB, then read back the WAL using `wlog.NewSegmentsReader` and decode `record.SamplesV2` entries to verify each `record.RefSample.ST` field matches the expected values.

## Verification

After fixing, ensure all of these pass:
- `go build ./tsdb/agent` -- code compiles
- `go vet ./tsdb/agent/...` -- no vet issues
- `go fmt ./tsdb/agent/...` -- properly formatted
- `go build ./tsdb/...` -- full TSDB compiles
- `go test -v -run TestCommit_AppendV2 ./tsdb/agent/` -- core AppendV2 tests
- `go test -v -run TestRollbackAppendV2 ./tsdb/agent/`
- `go test -v -run TestWALReplay_AppendV2 ./tsdb/agent/`
- `go test -v -run TestDB_EnableSTZeroInjection_AppendV2 ./tsdb/agent/`
- `go test -v -run TestDB_InvalidSeries_AppendV2 ./tsdb/agent/`

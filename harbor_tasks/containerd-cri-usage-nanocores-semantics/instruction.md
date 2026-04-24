# Fix CRI CPU Stats UsageNanoCores Semantics

## Problem

The Kubernetes e2e test `Summary API [NodeConformance] when querying /stats/summary should report resource usage through the stats api` fails when `PodAndContainerStatsFromCRI=true` is enabled.

The CRI stats plugin currently reports `UsageNanoCores: 0` as an authoritative value when there's not enough data to calculate an instantaneous CPU usage rate. This causes kubelet to treat the container as having actual zero CPU usage, when in reality the data is simply unavailable — indistinguishable from a container that genuinely has zero CPU usage.

## Expected Behavior

Mirror cAdvisor's `CpuInst` behavior: only report an instantaneous CPU rate when it can be computed from consecutive samples. When there's not enough data to compute a rate, the `UsageNanoCores` field must be left unset (nil) rather than set to 0.

Specifically:
- When there is no previous stats data (first sample), do not report a value
- When the time interval between samples is zero or negative, do not report a value
- When the CPU usage counter appears to go backwards (current < previous), do not report a value

## Technical Requirements

The implementation must satisfy all of the following:

1. **`getUsageNanoCores` return type**: The function must return `*uint64` (pointer to uint64) instead of `uint64`. This allows the function to distinguish between "zero CPU usage" and "no data available" by returning `nil` in the latter case.

2. **`nil` returns for missing data**: When any of the conditions above apply (first sample, zero/negative interval, backwards counter), the function must return `nil, nil` instead of `0, nil`.

3. **Caller nil checks**: Both callers of `getUsageNanoCores` (in container stats and sandbox stats) must check whether the returned pointer is `nil` before dereferencing and assigning to the `UsageNanoCores` field. Only assign the value when it is not `nil`.

4. **Error paths**: All error return paths must use `return nil, fmt.Errorf(...)` rather than `return 0, fmt.Errorf(...)`.

5. **Test helper function**: The test file needs a helper function to construct `*uint64` pointer values for test expectations (e.g., a function like `func uint64Ptr(v uint64) *uint64 { return &v }` or equivalent).

6. **Test expectations**: The test `TestContainerMetricsCPUNanoCoreUsage` must expect `nil` for `expectedNanoCoreUsageFirst` when there is no previous data to compute a rate, not `0`.

## Files Context

The CRI (Container Runtime Interface) server implementation is located in:
- `internal/cri/server/container_stats_list.go` - Container stats computation
- `internal/cri/server/sandbox_stats_linux.go` - Sandbox stats computation (Linux)
- `internal/cri/server/container_stats_list_test.go` - Tests including `TestContainerMetricsCPUNanoCoreUsage`
- `internal/cri/server/stats_collector.go` - Stats collector with `GetUsageNanoCores` method

## Validation

After the fix:
- `go build ./internal/cri/server/...` should succeed
- `go test -run TestContainerMetricsCPUNanoCoreUsage ./internal/cri/server/...` should pass
- `go vet ./internal/cri/server/...` should pass
- The CRI server core unit tests should pass

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`

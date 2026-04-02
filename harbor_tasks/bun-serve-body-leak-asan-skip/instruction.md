# Bug: serve-body-leak tests crash/timeout under ASAN builds

## Summary

The HTTP server body leak test suite at `test/js/bun/http/serve-body-leak.test.ts` is unreliable when Bun is compiled with AddressSanitizer (ASAN). The test suite measures RSS memory growth to detect body leaks by sending 10k warmup + 10k test requests (across 7 test cases = 140k requests total) with 512KB payloads and then asserting that memory stays below a threshold (512MB).

Under ASAN builds, this approach is fundamentally broken:

1. **Inflated RSS**: ASAN's quarantine zone (default 256MB) and allocator metadata add 2-3x memory overhead, inflating RSS well above the `end_memory <= 512MB` threshold even when there is no actual leak.

2. **Timeouts**: ASAN's instrumentation significantly slows execution, causing individual test cases to exceed the 40s/60s timeout limits when processing 20k requests per case.

3. **OOM kills**: The combined memory pressure from ASAN overhead plus the test's large payload volume causes the subprocess to get OOM-killed.

ASAN has its own built-in leak detection, so RSS-based memory leak detection is redundant and misleading under ASAN. These tests should be skipped on ASAN builds.

## Relevant files

- `test/js/bun/http/serve-body-leak.test.ts` — the test file that needs to be updated
- The `harness` module (importable as `"harness"` in test files) — provides platform/build detection utilities

## What to fix

The test cases in the `for` loop near the bottom of the file are guarded by `it.todoIf(skip || (isFlaky && isWindows))`. This condition needs to also skip when running under ASAN builds. The `harness` module exports detection flags for various build configurations.

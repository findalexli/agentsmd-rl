# Fix Flaky Benchmark Smoke Test

The benchmark smoke test in CI is failing intermittently with "TPS X.XX is below minimum threshold 1" even when the benchmark completes transactions successfully.

## Problem Analysis

The benchmark driver displays statistics including transactions per second (TPS). When the number of successful transactions is small relative to the benchmark duration (e.g., 1 transaction in 2 seconds), the calculated TPS should be a fractional value like 0.5. However, the current implementation appears to be truncating these fractional values to 0, causing the CI to reject runs that should pass.

Additionally, the CI workflow rejects any benchmark run with TPS below 1. This threshold is too strict for CI runners that may legitimately produce fractional TPS values between 0 and 1.

## Required Changes

You must modify:

1. **`crates/sui-benchmark/src/drivers/mod.rs`** - The benchmark driver's statistics display code. The TPS calculation needs to properly handle fractional values and display them with appropriate precision.

2. **`.github/workflows/rust.yml`** - The benchmark smoke test job's `--min-tps` threshold needs adjustment to accommodate slower CI runners.

## Success Criteria

After your changes:
- TPS values should display with 2 decimal places (e.g., "0.50" instead of "0")
- The benchmark driver should correctly calculate fractional TPS values without truncation
- The CI workflow's benchmark smoke test should accept TPS values as low as 0.01
- The code should compile and pass all lint checks (`cargo xclippy`, `cargo xlint`, `cargo fmt --check`)

## Agent Config Rules

From CLAUDE.md:
- All new files must start with the license header: `Copyright (c) Mysten Labs, Inc. SPDX-License-Identifier: Apache-2.0`
- Run `cargo xclippy` after finishing development
- Use `#[cfg(test)]` for test-only code
- Never disable or ignore tests
- Never use `#[allow(dead_code)]` or linting suppressions

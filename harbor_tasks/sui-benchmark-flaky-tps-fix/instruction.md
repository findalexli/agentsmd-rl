# Fix Flaky Benchmark Smoke Test

The benchmark smoke test in the CI is consistently flaky. It fails with "TPS X.XX is below minimum threshold 1" even when throughput should be acceptable.

## The Problem

The TPS (transactions per second) calculation in the benchmark driver has precision issues:

1. **Integer division bug**: The code uses `self.num_success_txes / self.duration.as_secs()` which is integer division. For example, if 1 transaction completes in 2 seconds, the TPS is 0 (1/2=0 in integer division), not 0.5.

2. **High threshold**: The CI workflow uses `--min-tps 1` which is too strict for slow CI runners that may produce ~0.5-1.0 TPS.

## Files to Modify

1. `crates/sui-benchmark/src/drivers/mod.rs` - Fix the TPS calculation in the `BenchmarkStats::report_table` method to use floating-point division and format to 2 decimal places

2. `.github/workflows/rust.yml` - Lower the `--min-tps` threshold in the benchmark smoke test job from 1 to 0.01

## What to Look For

In `crates/sui-benchmark/src/drivers/mod.rs`, find the code that calculates TPS for display:
- Look for `row.add_cell(Cell::new(self.num_success_txes / self.duration.as_secs()))`
- The fix should use `as_secs_f64()` for floating-point division and format the result to 2 decimal places

## Agent Config Rules

From CLAUDE.md:
- All new files must start with the license header: `Copyright (c) Mysten Labs, Inc. SPDX-License-Identifier: Apache-2.0`
- Run `cargo xclippy` after finishing development
- Use `#[cfg(test)]` for test-only code
- Never disable or ignore tests
- Never use `#[allow(dead_code)]` or linting suppressions

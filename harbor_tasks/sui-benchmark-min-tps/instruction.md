# Task: Add --min-tps Flag to sui-benchmark Stress Binary

## Problem
The sui-benchmark stress binary currently runs benchmarks but has no way to enforce a minimum throughput requirement. For CI smoke tests, we need the binary to exit with a non-zero status code if the achieved TPS (transactions per second) falls below a specified threshold.

## Task
Add a `--min-tps` command-line flag to the stress binary that:
1. Accepts an optional float value (e.g., `--min-tps 1.0`)
2. After the benchmark completes, calculates the actual TPS from `num_success_txes / duration`
3. If `actual_tps < min_tps`, returns an error with a clear message like "TPS {actual_tps:.2} is below minimum threshold {min_tps}"
4. The flag should be a global option available to all subcommands

## Files to Modify
- `crates/sui-benchmark/src/options.rs` - Add the `min_tps` field to the `Opts` struct
- `crates/sui-benchmark/src/bin/stress.rs` - Add the validation logic after benchmark completion

## Guidelines
- The project requires all files to have Apache-2.0 license headers with "Copyright (c) Mysten Labs, Inc."
- Use `cargo check --package sui-benchmark` to verify your changes compile
- The flag should use clap's `#[clap(long, global = true)]` attribute
- The TPS calculation should handle edge cases (avoid division by zero on very short durations)

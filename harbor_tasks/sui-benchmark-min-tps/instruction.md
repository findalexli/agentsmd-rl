# Task: Add --min-tps Flag to sui-benchmark Stress Binary

## Problem
The sui-benchmark stress binary currently runs benchmarks but has no way to enforce a minimum throughput requirement. For CI smoke tests, we need the binary to exit with a non-zero status code if the achieved TPS (transactions per second) falls below a specified threshold.

## Requirements

1. **Command-line option**: Add a `--min-tps` flag that accepts an optional float value and is available globally to all subcommands. The option must:
   - Be named `min_tps` in the code with type `Option<f64>`
   - Use the clap attribute `#[clap(long, global = true)]`
   - Include documentation explaining it specifies a minimum TPS threshold that, if not met, causes the binary to exit with an error

2. **TPS calculation and validation**: After the benchmark completes and statistics are available (specifically `num_success_txes` and `duration`), the code must:
   - Calculate actual TPS using `num_success_txes as f64 / duration.as_secs_f64()`
   - Handle edge cases (avoid division by zero on very short durations) by ensuring the denominator is at least 1.0
   - Compare the calculated TPS against the configured minimum threshold
   - If the actual TPS is below the minimum, return an error with the exact message format containing the text "is below minimum threshold" along with the actual and minimum TPS values
   - Use `anyhow::anyhow!` or `anyhow!` for the error return

3. **Implementation specifics**: The solution requires these exact code patterns:
   - Variable extraction: `let min_tps = opts.min_tps;`
   - Conditional check: `if let Some(min_tps) = min_tps`

4. **License headers**: Both modified files must include the standard license headers:
   - `SPDX-License-Identifier: Apache-2.0`
   - `Copyright (c) Mysten Labs, Inc.`

## Files to Modify
- `crates/sui-benchmark/src/options.rs` - add the command-line option definition
- `crates/sui-benchmark/src/bin/stress.rs` - add the TPS validation logic after benchmark completion

## Verification
- Use `cargo check --package sui-benchmark` to verify your changes compile

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo fmt (Rust formatter)`

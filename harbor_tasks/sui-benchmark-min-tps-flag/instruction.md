# Add --min-tps flag to sui-benchmark stress binary

## Problem

The `stress` binary in `sui-benchmark` package currently runs benchmarks but has no way to enforce a minimum TPS (transactions per second) threshold. When running in CI, we need the binary to exit with a non-zero status code if the achieved TPS falls below a specified minimum, so that performance regressions can be caught automatically.

## Requirements

Add support for a `--min-tps` command-line flag that:

1. Accepts an optional floating-point value representing the minimum acceptable TPS
2. After the benchmark completes, calculates the actual TPS from the number of successful transactions divided by the benchmark duration
3. If the actual TPS is below the specified minimum, the binary should exit with an error containing the message: `TPS {actual_tps:.2} is below minimum threshold {min_tps}`
4. Include a doc comment on the flag explaining: "If set, the stress binary will exit with a non-zero status code if the achieved TPS is below this threshold"

The benchmark stats contain:
- `num_success_txes: u64` - number of successful transactions
- `duration: Duration` - benchmark duration

## Testing

You can verify your implementation by:
1. Building the stress binary: `cargo build --package sui-benchmark --bin stress`
2. Checking the help output: `cargo run --package sui-benchmark --bin stress -- --help` (should show `--min-tps`)
3. Running cargo check: `cargo check --package sui-benchmark`

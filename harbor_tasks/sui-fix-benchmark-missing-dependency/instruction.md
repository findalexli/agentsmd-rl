# Fix MISSING_DEPENDENCY Panic in Move Language Benchmarks

## Problem

The Move language benchmarks in `external-crates/move/crates/language-benchmarks/` are failing at runtime with a `MISSING_DEPENDENCY` error. This happens when benchmarks try to use functions from the Move standard library (like `vector::empty`).

## Root Cause

Benchmark modules are currently declared at address `0x1` (the same address as the Move stdlib). When the benchmark publishes its compiled modules at address `0x1`, it overwrites the stdlib that was already there. This causes any benchmark that uses stdlib functions to fail with `MISSING_DEPENDENCY` at runtime.

## Your Task

Fix the benchmarks so they can successfully use stdlib functions without overwriting them. The fix involves:

1. **Move benchmark modules to a new address**: Change the module address from `0x1` to `0x2` in all `.move` files
2. **Update the Rust code**: Modify the benchmark harness to:
   - Define a new `BENCH_ADDR` constant for address `0x2`
   - Add a `publish_stdlib()` helper function that publishes the compiled stdlib at address `0x1`
   - Update `compile_modules()` to use a named address for the bench module
   - Ensure `publish_stdlib()` is called before executing benchmarks

## Files to Modify

- `external-crates/move/crates/language-benchmarks/src/move_vm.rs` - Main harness code
- `external-crates/move/crates/language-benchmarks/benches/criterion.rs` - Benchmark runner
- `external-crates/move/crates/language-benchmarks/tests/*.move` - Move benchmark files (8 files)

## Expected Behavior

After your fix:
- `cargo bench -p language-benchmarks` should run without `MISSING_DEPENDENCY` panics
- Benchmarks using stdlib functions (vector, transfers, natives) should work correctly
- The stdlib should be published at `0x1`, and benchmark modules at `0x2`

## Testing

Run the benchmarks to verify the fix:
```bash
cargo bench -p language-benchmarks
```

The benchmarks should complete without panicking.

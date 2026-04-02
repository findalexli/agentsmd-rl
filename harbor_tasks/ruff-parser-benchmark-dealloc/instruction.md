# Parser Benchmarks Include AST Deallocation Time

## Problem

The parser benchmarks in `crates/ruff_benchmark/benches/parser.rs` are measuring more than just parsing time. Currently, the benchmark closure uses `b.iter()` which includes the time to deallocate the parsed AST in the measurement. This means the reported benchmark numbers include deallocation overhead, which isn't what we want to measure — we only care about parsing speed.

Additionally, the benchmark includes a `CountVisitor` that walks the entire AST and counts statements. This visitor was originally added to prevent the compiler from optimizing away the parse result, but it adds unnecessary overhead to the measurement that has nothing to do with parsing performance.

## Expected Behavior

The parser benchmarks should measure **only** the time spent parsing Python source code. Deallocation of the resulting AST and any post-parse processing should not be included in the measurement.

## Relevant Files

- `crates/ruff_benchmark/benches/parser.rs` — the parser benchmark file

## Hints

- Look at criterion's API for benchmark methods that handle large return values differently
- Dead code and unused imports should be cleaned up

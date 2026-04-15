# Task: deno-chore-remove-some-top-level

## Problem

The Deno repository root contains entries that should be relocated:
- `bench_util/` directory at the top level should be moved under `tests/`
- `docs/tsgo.md` duplicates documentation that should live with the TypeScript compiler code

Additionally, the linting script `tools/lint.js` only tracks top-level **files** and misses top-level **directories**.

## Requirements

### 1. Move `bench_util/` to `tests/bench_util/`
- The `bench_util` directory must be relocated from the repo root to `tests/bench_util/`
- The `Cargo.toml` workspace members must be updated to reflect the new path
- The `deno_bench_util` path dependency must point to the new location
- After the move, `cargo check -p deno_bench_util` must pass

### 2. Move `docs/tsgo.md` content
- The `docs/tsgo.md` file must be deleted
- Its content must appear in `cli/tsc/README.md`
- After the move, `cli/tsc/README.md` must contain the "Typescript-Go Integration" section and the typescript-go client rust content

### 3. Update `tools/lint.js` to handle directories
- The linting script must detect top-level **directories** (not just files) as entries
- It must correctly identify `cli`, `tests`, and `tools` as valid top-level entries
- It must continue to block unauthorized new top-level entries

## Verification

After making the changes:
1. `cargo check -p deno_bench_util` must pass
2. `tests/bench_util/` must exist and contain `Cargo.toml`
3. `bench_util/` must not exist at the repo root
4. `docs/tsgo.md` must not exist
5. `cli/tsc/README.md` must contain the transferred documentation
6. The linting script must recognize `cli`, `tests`, `tools` (and other existing directories) as valid top-level entries

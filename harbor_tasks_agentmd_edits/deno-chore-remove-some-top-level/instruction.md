# chore: remove some top level entries from repo

## Problem

The Deno repository root is becoming cluttered. The `bench_util` directory at the top level is actually only used for tests and should be moved into `tests/`. Additionally, the `docs/tsgo.md` file duplicates information that should live with the TypeScript compiler code. The `tools/lint.js` script also needs to be updated to track both top-level directories AND files (not just files).

## Expected Changes

1. **Move `bench_util/` to `tests/bench_util/`**
   - Move the entire `bench_util` directory to `tests/bench_util/`
   - Update `Cargo.toml` workspace members (remove `bench_util`, add `tests/bench_util`)
   - Update `deno_bench_util` path dependency to point to `./tests/bench_util`

2. **Move `docs/tsgo.md` content**
   - Delete `docs/tsgo.md`
   - Append its content to `cli/tsc/README.md`

3. **Update `tools/lint.js`**
   - Rename `listTopLevelFiles()` to `listTopLevelEntries()`
   - Update the logic to extract the first path component (directory name) for files within directories
   - Rename `ensureNoNewTopLevelFiles()` to `ensureNoNewTopLevelEntries()`
   - Expand the allowed list to include directories: `.cargo`, `.devcontainer`, `.github`, `cli`, `ext`, `libs`, `runtime`, `tests`, `tools`
   - Use a `Set` instead of array for O(1) lookups

## Files to Look At

- `Cargo.toml` — workspace configuration
- `tools/lint.js` — the lint script that needs refactoring
- `docs/tsgo.md` — documentation file to be moved
- `cli/tsc/README.md` — destination for the documentation

## Verification

After the changes:
- `cargo check -p deno_bench_util` should pass
- The lint.js logic should correctly identify `cli`, `tests`, `tools` as top-level entries
- The workspace should compile successfully

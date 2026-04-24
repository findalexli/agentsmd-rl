# Fix sui-framework UPDATE Build Order

## Problem

When running tests with `UPDATE=1`, the current implementation deletes existing compiled packages, docs, and API files **before** the build runs. If the build fails, these files are permanently lost.

## Expected Behavior

Files should only be deleted **after** a successful build. If the build fails, the original files must remain intact.

## File to Modify

`crates/sui-framework/tests/build-system-packages.rs` — the `build_system_packages` async test function

## Constants Used

The test uses these constants (defined in the file):
- `CRATE_ROOT` — crate root path
- `COMPILED_PACKAGES_DIR` — compiled packages directory name
- `DOCS_DIR` — docs directory name
- `PUBLISHED_API_FILE` — published API file name

## Verification

After the fix:
1. `cargo check -p sui-framework --tests` should pass
2. When `UPDATE=1` is set, the build completes to a temporary directory first, then files are safely updated

## Hint

If the build fails, the original files must remain untouched. The deleted files should only exist if the build succeeded.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`

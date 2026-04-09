# Fix sui-framework UPDATE Behavior

## The Problem

In `crates/sui-framework/tests/build-system-packages.rs`, there's an async test `build_system_packages` that builds Move packages and can update checked-in files when run with `UPDATE=1` environment variable.

**The bug**: When `UPDATE=1` is set, the test deletes existing compiled packages, docs, and API files **before** attempting to build. This means if the build fails (e.g., due to a compilation error), the existing files are already gone, leaving the repo in a broken state.

**What should happen**: The test should build to a temporary directory first, and only delete and replace the existing files if the build succeeds.

## Your Task

Fix the order of operations in `crates/sui-framework/tests/build-system-packages.rs`:

1. Always build to a temporary directory first (don't conditionally set `out_dir` based on UPDATE)
2. After a successful build, check if UPDATE is set
3. If UPDATE is set: delete existing files (with existence checks), then copy the newly built files from temp dir
4. Run the diff check against the crate root

## Files to Modify

- `crates/sui-framework/tests/build-system-packages.rs` - The test function `build_system_packages`

## Key Constants

The test uses these constants defined at the top of the file:
- `COMPILED_PACKAGES_DIR = "packages_compiled"`
- `DOCS_DIR = "docs"`
- `PUBLISHED_API_FILE = "published_api.txt"`

## Requirements

- The fix must preserve the existing license header (already present)
- All existing tests should still work
- The code should compile with `cargo check --test build-system-packages -p sui-framework`
- Follow the existing code style in the file

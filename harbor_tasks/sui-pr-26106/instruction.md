# Task: Fix sui-framework UPDATE Build Order

## Problem

When running the `build-system-packages` test with `UPDATE=1`, the current implementation **deletes the existing compiled packages, docs, and API files BEFORE the build runs**. If the build fails, these files are lost and the user has to regenerate them from scratch or restore from git.

This is particularly frustrating during development when builds frequently fail due to compilation errors.

## Current Behavior (Bug)

In `crates/sui-framework/tests/build-system-packages.rs`, when `UPDATE=1` is set:

1. The code deletes `packages_compiled/`, `docs/`, and `published_api.txt` from the crate root
2. Then it runs the build
3. If the build fails, the deleted files are gone

## Expected Behavior (Fix)

The build should:

1. **Always build to a temporary directory first** (`tempdir.path()`)
2. Run the full build process
3. **Only after successful build**, delete the old files and copy the new ones from tempdir
4. Include safety checks like verifying paths exist before attempting deletion

## Key Changes Required

The `build_system_packages()` async test function needs restructuring:

1. Change `out_dir` to **always** use `tempdir.path()` (remove the conditional)
2. Move the file deletion logic to **after** the `build_packages().await` call
3. Add existence checks before deletion (`if p.exists()`)
4. After deletion, copy the newly built files from tempdir to crate root using `fs_extra::dir::copy`

## Files to Modify

- `crates/sui-framework/tests/build-system-packages.rs`

## Testing

The fix can be verified by:
1. Running `cargo check -p sui-framework --tests` to ensure compilation passes
2. The key behavioral change is the order: build completes first, then files are deleted/copied

## Reference

Look for the `UPDATE` environment variable handling in the `build_system_packages` test function. The current logic deletes files at the start when `UPDATE` is set - this needs to move to after the build succeeds.

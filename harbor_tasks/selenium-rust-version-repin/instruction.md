# Fix Rust Pre-Release Dependency Repin

## Problem

The Rust pre-release workflow has a bug where cargo dependencies are not automatically repinned after version updates. This can leave the `Cargo.Bazel.lock` file in a stale state, causing Bazel to detect a mid-evaluation file-hash conflict and crash during the build process.

The issue occurs in the `rust:version` rake task in `rake_tasks/rust.rake`. After updating version numbers in `rust/Cargo.toml` and `rust/BUILD.bazel`, the task should immediately repin cargo dependencies to ensure the lockfile stays synchronized.

## Current Behavior

- The `rust:version` task updates version strings in files
- The `rust:update` task (which runs `CARGO_BAZEL_REPIN=true`) exists separately
- During pre-release, these tasks were being called separately via a complex conditional in the GitHub workflow
- This separation can cause Bazel to read the lockfile twice with different hashes, causing a crash

## Expected Behavior

After the `rust:version` task updates version files, it should automatically invoke `rust:update` to repin dependencies immediately, before any other operations can occur.

## Files to Modify

1. **`rake_tasks/rust.rake`** - Add automatic `rust:update` invocation at the end of the `version` task
2. **`.github/workflows/pre-release.yml`** (optional) - Simplify the update command since rust:update is now automatic

## Key Considerations

- The `rust:update` task may have already been called in the same Ruby process, so you'll need to use `Rake::Task['rust:update'].reenable` before invoking it again
- The fix should include a comment explaining why this is necessary (mid-evaluation file-hash conflict in Bazel)
- The comment should mention `CARGO_BAZEL_REPIN` to clarify what operation is being performed

## Testing

You can verify the syntax of your changes with:
```bash
ruby -c rake_tasks/rust.rake
```

The rake tasks can be explored with:
```bash
./go -T rust
```

## References

- The `rust:update` task runs: `CARGO_BAZEL_REPIN=true bazel fetch @crates//:all`
- See `rust/AGENTS.md` for Rust-specific guidance
- See root `AGENTS.md` for general repo guidance on dependency updates / repin flows (marked as high risk)

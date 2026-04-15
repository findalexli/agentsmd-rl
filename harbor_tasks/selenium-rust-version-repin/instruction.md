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

1. **`rake_tasks/rust.rake`** — the `version` task must be modified to automatically invoke `rust:update` after version files are updated
2. **`.github/workflows/pre-release.yml`** — the update command should be simplified since `rust:update` is now automatic

## Required Implementation Details

The `rake_tasks/rust.rake` file must contain all of the following after modification:

1. The exact string `Rake::Task['rust:update'].reenable`
2. The exact string `Rake::Task['rust:update'].invoke`
3. A comment containing the exact phrase: `Repin cargo immediately after updating the version`
4. The comment must mention `CARGO_BAZEL_REPIN`
5. The comment must explain the mid-evaluation file-hash conflict (mention either `mid-evaluation` or `file-hash conflict`)
6. The `Rake::Task['rust:update'].reenable` call must appear before `Rake::Task['rust:update'].invoke`
7. The `invoke` call must be inside the `version` task block (within the `task :version ... do ... end` structure)
8. The Ruby syntax must be valid: `ruby -c rake_tasks/rust.rake` should pass

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

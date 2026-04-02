# Build churn when using Jujutsu (jj) VCS

## Bug

When developing `uv` inside a [Jujutsu](https://martinvonz.github.io/jj/) repository, every `cargo build` triggers a full rebuild of the `uv-cli` crate — even when no source code has changed.

The root cause is in `crates/uv-cli/build.rs`, specifically the `commit_info` function. This function retrieves git commit metadata (hash, date, tag distance) and sets `cargo:rerun-if-changed` on git internal files. In a jj-managed repo, jj snapshots the working copy very frequently, which causes the git state files to change constantly — triggering Cargo to re-run the build script and recompile the crate on every build.

The existing code already has an early-return guard that skips commit info retrieval when there is no `.git` directory (i.e., not a git repo at all). However, there is no analogous guard for jj repositories, which store their metadata in a `.jj` directory at the workspace root.

## Expected behavior

When the workspace root contains a `.jj` directory (indicating a jj repository), the `commit_info` function should skip all git-related operations and return early — the same way it does when `.git` is absent. This avoids unnecessary rebuilds caused by jj's frequent snapshots.

## Relevant files

- `crates/uv-cli/build.rs` — the `commit_info` function

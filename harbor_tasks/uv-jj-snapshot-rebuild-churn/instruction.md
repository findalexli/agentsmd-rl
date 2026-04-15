# Build churn when using Jujutsu (jj) VCS

## Bug

When developing `uv` inside a [Jujutsu](https://martinvonz.github.io/jj/) repository, every `cargo build` triggers a full rebuild of a crate — even when no source code has changed.

Jujutsu (jj) is a VCS that frequently snapshots the working copy. One of the crates in this project has a build script that retrieves git commit metadata (hash, date, tag distance) and sets `cargo:rerun-if-changed` directives on git internal files. In a jj-managed repository, jj's frequent snapshots cause these git state files to change constantly, which triggers Cargo to re-run the build script and recompile the crate on every build.

## Expected behavior

When the workspace root contains a `.jj` directory (indicating a jj repository), the build script should avoid performing the git-related operations that cause unnecessary rebuilds. Existing git functionality should be preserved when not in a jj repository.

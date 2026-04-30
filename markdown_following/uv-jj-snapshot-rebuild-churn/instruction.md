# Build churn when using Jujutsu (jj) VCS

## Bug

When developing `uv` inside a [Jujutsu](https://martinvonz.github.io/jj/) repository, every `cargo build` triggers a full rebuild of a crate — even when no source code has changed.

Jujutsu (jj) is a VCS that frequently snapshots the working copy. The `uv-cli` crate has a build script (`build.rs`) that retrieves git commit metadata (hash, date, tag distance) via the `commit_info` function and sets `cargo:rerun-if-changed` directives on git internal files. In a jj-managed repository, jj's frequent snapshots cause these git state files to change constantly, which triggers Cargo to re-run the build script and recompile the crate on every build.

## Expected behavior

When the workspace root contains a `.jj` directory (indicating a jj repository), the `commit_info` function should avoid performing the git-related operations that cause unnecessary rebuilds. Specifically:

1. Check if the workspace root contains a `.jj` directory before performing git operations
2. If `.jj` exists, skip the git metadata retrieval and return early
3. Existing git functionality should be preserved when not in a jj repository, including:
   - Git detection (looking for `.git` directory)
   - Git command execution (via `Command::new("git")`)
   - The `git_head` helper function
   - Environment variable setting (`UV_COMMIT_*` variables)
   - `cargo:rerun-if-changed` directives on git files

## Implementation constraints

Any code changes must follow the project's CLAUDE.md conventions:
- Avoid `.unwrap()`, `panic!`, `unreachable!`, and `unsafe` blocks in new code
- Use descriptive variable names (not single-character names)
- Use `#[expect(...)]` instead of `#[allow(...)]` for any clippy suppressions

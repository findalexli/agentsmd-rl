# Fix Cargo.lock in uv-build source distributions

## Problem

When building `uv-build` from a maturin-generated source distribution (sdist), `cargo build --locked` fails. The error reports that `Cargo.lock` references packages that are not present in the sdist.

This happens because maturin copies the full workspace `Cargo.lock` into the sdist tarball, but the sdist only contains a subset of workspace crates (just `uv-build` and its local dependencies). The lockfile still references every other workspace member (`uv`, `uv-resolver`, `uv-client`, etc.), making it inconsistent with the crates actually shipped in the sdist.

## Expected Behavior

There should be a script at `scripts/repair-sdist-cargo-lock.py` that can be run on a maturin-generated `.tar.gz` sdist to fix this problem. The script should:

1. Accept the path to the sdist tarball as a CLI argument
2. Extract the tarball and locate the `Cargo.lock` inside it
3. Prune the lockfile so it only contains packages needed by the included crates
4. Verify the lockfile is consistent (e.g., `cargo metadata --locked` succeeds)
5. Repack the tarball in-place

The script should validate its input and exit with a non-zero status if the file is not a valid tarball, contains an unexpected structure (e.g., multiple top-level directories), or is missing a `Cargo.lock`.

## Files to Look At

- `scripts/` — other build-related Python scripts in this directory for style reference (e.g., `scripts/patch-dist-manifest-checksums.py`)
- `.github/workflows/build-release-binaries.yml` — the release workflow that builds the sdist; the new script should be invoked after `maturin sdist`
- `crates/uv-build/Cargo.toml` — the crate whose sdist has the broken lockfile

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`

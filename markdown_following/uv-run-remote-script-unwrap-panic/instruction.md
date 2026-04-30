# Bug: `uv run` panics on remote script due to unsafe `.unwrap()` call

## Summary

When executing a remote Python script via `uv run https://example.com/script.py`, the process can panic at runtime. The downloaded temporary file is managed separately from the command that uses it, and the code assumes the file will always be present.

## Problem

In the current code, when a remote script URL is provided:

1. The `PythonRemote` variant of the `RunCommand` enum is defined as `PythonRemote(DisplaySafeUrl, Vec<OsString>)` — it stores only the remote URL, not the downloaded file.
2. The downloaded file is passed separately as `downloaded_script: Option<&tempfile::NamedTempFile>` and threaded through the call chain:
   - `run_project()` in `crates/uv/src/lib.rs` accepts `downloaded_script` as a parameter
   - `run()` in `crates/uv/src/commands/project/run.rs` accepts `downloaded_script` as a parameter
   - `as_command()` on `RunCommand` accepts `downloaded_script: Option<&tempfile::NamedTempFile>` and calls `.unwrap()` on it in the `PythonRemote` match arm
3. Since `downloaded_script` is an `Option`, the type system does not guarantee it is present when `.unwrap()` is called, causing a potential panic.

## Expected behavior

The code should be restructured so that by the time command execution occurs, the downloaded file is guaranteed to be available. The `.unwrap()` call on the downloaded script in `as_command()` must be eliminated, and the `downloaded_script` parameter should not need to be separately threaded through `run()` and `run_project()`. The `PythonRemote` variant should not store only a `DisplaySafeUrl`.

## Relevant files

- `crates/uv/src/commands/project/run.rs` — `RunCommand` enum and command execution
- `crates/uv/src/lib.rs` — `run()` and `run_project()` functions
- `crates/uv/src/commands/mod.rs` — module re-exports

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo fmt (Rust formatter)`

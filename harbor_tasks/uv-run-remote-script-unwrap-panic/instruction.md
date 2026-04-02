# Bug: `uv run` panics on remote script due to unwrap on downloaded file

## Summary

When executing a remote Python script via `uv run https://example.com/script.py`, the downloaded temporary file is threaded through several function layers as an `Option<&tempfile::NamedTempFile>`. In the `as_command` method of `RunCommand` (in `crates/uv/src/commands/project/run.rs`), this option is unconditionally unwrapped — which can panic if the value is `None`.

## Problem

The `RunCommand` enum has a `PythonRemote` variant that stores the remote URL, but the actual downloaded script file is managed separately and passed as a loose `Option` parameter through:

1. `run_project()` in `crates/uv/src/lib.rs`
2. `run()` in `crates/uv/src/commands/project/run.rs`
3. `as_command()` in the same file

The `as_command()` method calls `.unwrap()` on this optional downloaded script, which is unsound — the type system doesn't guarantee the download has happened before execution.

Additionally, `RunCommand::from_args()` creates a `PythonRemote` variant with just a URL, but the download and PEP 723 metadata parsing logic lives far away in `lib.rs`, making the state machine implicit and fragile.

## Expected behavior

The type system should enforce that by the time a command is executed, any remote script has already been downloaded. There should be no `.unwrap()` on the downloaded script file. The command parsing and resolution lifecycle should make it impossible to reach execution without the download being complete.

## Relevant files

- `crates/uv/src/commands/project/run.rs` — `RunCommand` enum, `from_args()`, `as_command()`
- `crates/uv/src/lib.rs` — `run()` and `run_project()` functions that wire everything together
- `crates/uv/src/commands/mod.rs` — re-exports from the `run` module

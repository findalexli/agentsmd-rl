# Bug: `uv run` panics on remote script due to unsafe handling of downloaded file

## Summary

When executing a remote Python script via `uv run https://example.com/script.py`, the process can panic. The downloaded temporary file is passed through several function layers, and the code that consumes it does not have a safe fallback when the file is absent.

## Problem

The `RunCommand` enum has a `PythonRemote` variant that stores a remote URL, but the corresponding downloaded script file is managed separately. The `as_command()` method calls `.unwrap()` on this optional value, which can panic.

The command parsing and resolution lifecycle makes it possible to reach execution without the download being complete — the type system does not enforce that the file exists before it is used.

## Expected behavior

The type system should enforce that by the time a command is executed, any remote script has already been downloaded. There should be no `.unwrap()` call on the downloaded script file. The command parsing and resolution lifecycle should make it impossible to reach execution without the download being complete.

## Behavioral requirements (tested)

The tests verify the following structural constraints:
- The `run()` function in `crates/uv/src/commands/project/run.rs` must not have a `downloaded_script` parameter.
- The `as_command()` method must not take `downloaded_script` as an `Option` parameter.
- The `run_project()` function in `crates/uv/src/lib.rs` must not have a `downloaded_script` parameter.
- The `PythonRemote` variant in the `RunCommand` enum must not hold only a URL — it must embed a file type.
- The `as_command()` method must not call `.unwrap()` on a downloaded script.

## Relevant files

- `crates/uv/src/commands/project/run.rs` — `RunCommand` enum and command execution
- `crates/uv/src/lib.rs` — `run()` and `run_project()` functions
- `crates/uv/src/commands/mod.rs` — module re-exports

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo fmt (Rust formatter)`

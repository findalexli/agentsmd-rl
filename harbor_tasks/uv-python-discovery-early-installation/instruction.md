## Refactor: Construct PythonInstallation early in the discovery pipeline

## Problem

The Python discovery pipeline passes around raw `(PythonSource, Interpreter)` tuples through several internal functions, only converting them to the `PythonInstallation` struct at the very end. This creates unnecessary complexity:

1. Internal helper functions return iterators over `(PythonSource, Interpreter)` tuples.
2. Each call site at the end of the discovery pipeline has to destructure tuples to access `source` and `interpreter` fields, then wrap the result using a conversion helper method.
3. A `from_tuple` conversion method on `PythonInstallation` exists solely to bridge this gap, adding boilerplate that could be eliminated.

## Task

Refactor the internal discovery functions so that `PythonInstallation` is constructed **before** the final call site, eliminating the tuple-then-convert pattern. Specifically:

- Three internal helper functions that currently return `impl Iterator<Item = Result<(PythonSource, Interpreter), Error>>` should be changed to return `impl Iterator<Item = Result<PythonInstallation, Error>>` instead
- The helper that lazily converts executables into interpreters should construct `PythonInstallation` struct literals directly rather than returning `(PythonSource, Interpreter)` tuples
- The `from_tuple` conversion method on `PythonInstallation` should be removed entirely
- Any closures that currently use tuple destructuring patterns like `|(source, interpreter)|` to access fields should be updated to use `.source` and `.interpreter` field access on `PythonInstallation` instead
- The public entry point for finding Python installations must remain public and continue to return `Result<PythonInstallation, Error>`

The relevant code is in the Python discovery pipeline. The `PythonInstallation` struct has `source` and `interpreter` fields that should be populated directly rather than via tuple conversion.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`

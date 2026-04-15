## Refactor: Construct PythonInstallation early in the discovery pipeline

## Problem

The Python discovery pipeline in `crates/uv-python/src/discovery.rs` passes around raw `(PythonSource, Interpreter)` tuples through several internal functions, only converting them to the `PythonInstallation` struct at the very end of `find_python_installations`. This creates unnecessary complexity:

1. Internal helper functions return iterators over `(PythonSource, Interpreter)` tuples.
2. Each call site in `find_python_installations` has to destructure tuples to access `source` and `interpreter` fields, then wrap the result in `PythonInstallation::from_tuple(tuple)` at the boundary.
3. The `from_tuple` conversion method on `PythonInstallation` (in `crates/uv-python/src/installation.rs`) exists solely to bridge this gap.

## What to do

Refactor the internal discovery functions so that `PythonInstallation` is constructed **before** the final call site, eliminating the tuple-then-convert pattern. Concretely:

- Rename and retype three internal helpers so they return `impl Iterator<Item = Result<PythonInstallation, Error>>` directly:
  - `python_interpreters` → `python_installations`
  - `python_interpreters_from_executables` → `python_installations_from_executables`
  - `python_interpreters_with_executable_name` → `python_installations_with_executable_name`
- Update closures inside these helpers to use `.source` and `.interpreter` field access on `PythonInstallation` instead of tuple destructuring (`|(source, interpreter)|`)
- Inside `python_installations_from_executables`, construct a `PythonInstallation { source, interpreter }` struct literal instead of returning a tuple
- Remove the `from_tuple` conversion method from `PythonInstallation` in `crates/uv-python/src/installation.rs`
- Update closures in `find_python_installations` that call the renamed helpers to use `.source` and `.interpreter` field access instead of `PythonInstallation::from_tuple(tuple)`
- `find_python_installations` must remain public and continue to return `Result<PythonInstallation, Error>`

The relevant source file is `crates/uv-python/src/discovery.rs` and the `PythonInstallation` struct is defined in `crates/uv-python/src/installation.rs`.

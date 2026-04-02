# Refactor: Construct PythonInstallation early in the discovery pipeline

## Problem

The Python discovery pipeline in `crates/uv-python/src/discovery.rs` passes around raw `(PythonSource, Interpreter)` tuples through several internal functions, only converting them to the `PythonInstallation` struct at the very end of `find_python_installations`. This creates unnecessary complexity:

1. Internal helper functions like `python_interpreters()`, `python_interpreters_from_executables()`, and `python_interpreters_with_executable_name()` all return iterators over `(PythonSource, Interpreter)` tuples.

2. Each call site in `find_python_installations` has to destructure tuples to access `source` and `interpreter` fields, then wrap the result in `PythonInstallation::from_tuple(tuple)` at the boundary.

3. The `from_tuple` conversion method on `PythonInstallation` (in `crates/uv-python/src/installation.rs`) exists solely to bridge this gap.

## What to do

Refactor the internal discovery functions to construct and return `PythonInstallation` directly instead of `(PythonSource, Interpreter)` tuples. This should:

- Update the internal functions to return `PythonInstallation` instead of tuples
- Update all closures that destructure `(source, interpreter)` to work with `PythonInstallation` field access
- Remove the now-unnecessary `from_tuple` conversion method
- Update function names and doc comments to match the new semantics

The relevant functions are in `crates/uv-python/src/discovery.rs` and `PythonInstallation` is defined in `crates/uv-python/src/installation.rs`.

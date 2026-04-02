# Code duplication: `is_explicit` logic for `PythonSource` is inline in `allows_installation`

## Summary

In `crates/uv-python/src/discovery.rs`, the `PythonPreference::allows_installation` method contains an inline match expression that determines whether a `PythonSource` is "explicit" (i.e., directly provided by the user or an active virtual environment). This logic is implemented as a local `let is_explicit = match source { ... }` block inside `allows_installation`.

## Problem

The knowledge of which `PythonSource` variants are "explicit" is a property of `PythonSource` itself, not of its callers. Having this logic inline in `allows_installation` means:

1. If a new variant is added to `PythonSource`, the developer must find and update this inline match — it's not colocated with the enum definition
2. The logic cannot be reused by other methods that may need to check explicitness
3. The match arms are separated from the other `PythonSource` methods like `is_maybe_system()`, making the code harder to navigate

## Relevant Code

Look at the `PythonPreference::allows_installation` method in `crates/uv-python/src/discovery.rs`. The inline match for `is_explicit` should be refactored to live alongside the other `PythonSource` methods (like `is_maybe_system`).

The method should handle all current variants of `PythonSource`:
- `ProvidedPath`, `ParentInterpreter`, `ActiveEnvironment`, `CondaPrefix` — these are explicit
- `Managed`, `DiscoveredEnvironment`, `SearchPath`, `SearchPathFirst`, `Registry`, `MicrosoftStore`, `BaseCondaPrefix` — these are not explicit

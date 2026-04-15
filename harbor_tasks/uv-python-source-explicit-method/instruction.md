# Inline variant classification in `allows_installation`

## Summary

In `crates/uv-python/src/discovery.rs`, the `PythonPreference::allows_installation` method contains inline logic that classifies `PythonSource` variants to determine whether they are "explicit" — meaning directly provided by the user or from an active virtual environment. This classification should instead be a method on `PythonSource` itself.

## Problem

The classification logic is embedded within `allows_installation` as an inline match over `PythonSource` variants, rather than being part of the `PythonSource` type's own API. This means:

1. Other code that needs to know whether a source is explicit cannot reuse the classification
2. The classification is not discoverable from the `PythonSource` type definition
3. Adding new `PythonSource` variants requires locating and updating the inline logic in `allows_installation`

## Expected Behavior

The `PythonSource` enum should expose a `pub(crate) fn is_explicit(&self) -> bool` method that returns:

- `true` for: `ProvidedPath`, `ParentInterpreter`, `ActiveEnvironment`, `CondaPrefix`
- `false` for: `Managed`, `DiscoveredEnvironment`, `SearchPath`, `SearchPathFirst`, `Registry`, `MicrosoftStore`, `BaseCondaPrefix`

The method should be documented with a comment explaining what "explicit" means.

The `allows_installation` method should no longer contain inline variant-matching logic for the explicitness check — it should call the new method on `PythonSource` instead.

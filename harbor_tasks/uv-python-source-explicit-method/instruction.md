# Inline variant classification in installation preference logic

## Problem

The codebase contains inline logic that classifies `PythonSource` variants to determine whether a source is "explicit" — meaning directly provided by the user or from an active virtual environment. This inline classification logic is embedded within a method that checks whether Python installations are allowed, rather than being part of the `PythonSource` type's own API.

This creates several maintainability issues:

1. Other code that needs to know whether a source is explicit cannot reuse the classification
2. The classification is not discoverable from the `PythonSource` type definition
3. Adding new `PythonSource` variants requires locating and updating the inline logic in the installation preference check

## Classification Requirements

A source is "explicit" (returns `true`) if it is one of:
- `ProvidedPath`
- `ParentInterpreter`
- `ActiveEnvironment`
- `CondaPrefix`

A source is not "explicit" (returns `false`) if it is one of:
- `Managed`
- `DiscoveredEnvironment`
- `SearchPath`
- `SearchPathFirst`
- `Registry`
- `MicrosoftStore`
- `BaseCondaPrefix`

## Expected Behavior

The classification logic should be refactored so that:

1. The `PythonSource` type exposes a query method that returns whether a source is "explicit"
2. The method has appropriate visibility for use across the crate
3. The method includes documentation explaining what "explicit" means
4. The installation preference logic no longer contains inline variant-matching for the explicitness check — it should delegate to the new query method on `PythonSource` instead

# Inconsistent Python preference enforcement across commands

## Problem

The `PythonPreference` enforcement logic (which controls whether managed, system, or both kinds of Python installations are allowed) is scattered across multiple locations with subtly different behavior:

1. **`crates/uv-python/src/discovery.rs`** has a free function that checks whether a given interpreter satisfies the preference. It correctly handles "explicit" sources (active environments, provided paths, conda prefixes) — these are always allowed regardless of the preference setting.

2. **`crates/uv/src/commands/python/list.rs`** has an inline `match` on `PythonPreference` that does its own filtering, but does NOT account for explicit sources. This means `uv python list` with `--python-preference only-managed` incorrectly filters out active environments.

3. **`crates/uv/src/commands/project/mod.rs`** calls the free function directly, coupling it to a specific API that should be encapsulated on the type.

4. There is also a standalone helper function in `discovery.rs` for checking whether an installation is system-managed, which duplicates logic that should live on the installation type.

## Expected behavior

The preference enforcement should be consolidated into methods on the relevant types (`PythonPreference` and `PythonInstallation`), ensuring consistent behavior across all commands. Each call site should use the same consolidated method rather than reimplementing the logic.

## Files involved

- `crates/uv-python/src/discovery.rs` — preference-checking free functions and the `PythonPreference` impl block
- `crates/uv-python/src/installation.rs` — `PythonInstallation` struct
- `crates/uv-python/src/lib.rs` — public re-exports
- `crates/uv/src/commands/project/mod.rs` — environment usability check
- `crates/uv/src/commands/python/list.rs` — inline preference filtering

## Hints

- The `PythonInstallation` type already has `source` and `interpreter` fields that contain everything needed for preference checking.
- Explicit sources should always be allowed, even when they conflict with the preference.
- The `Interpreter::is_managed()` method already exists and checks if the base prefix is in a managed location.
- Look at how `PythonPreference` already has a method for checking source-level allowance — consider what additional methods are needed for interpreter-level and installation-level checks.

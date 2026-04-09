# [ty] Reject unsupported python-version values in configuration files

## Problem

When a user specifies an unsupported Python version (like `2.7` or `3.6`) in the `environment.python-version` setting in their `pyproject.toml` or `ty.toml` configuration file, `ty` silently accepts it. This is inconsistent with the CLI, which already rejects unsupported versions. The configuration file parser should enforce the same validation.

For example, this configuration should be rejected but currently isn't:

```toml
[tool.ty.environment]
python-version = "2.7"
```

## Expected Behavior

When an unsupported `python-version` value is specified in a configuration file, `ty` should reject it at parse time with a clear error message indicating which versions are supported. The supported versions are those returned by `PythonVersion::iter()`.

## Files to Look At

- `crates/ty_project/src/metadata/options.rs` — Contains `EnvironmentOptions` struct where the `python_version` field is deserialized from configuration files. The serde deserialization for this field needs to validate against the set of supported Python versions.

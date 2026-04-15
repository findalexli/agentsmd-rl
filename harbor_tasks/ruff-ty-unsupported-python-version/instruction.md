# [ty] Reject unsupported python-version values in configuration files

## Problem

When a user specifies an unsupported Python version (like `2.7` or `3.6`) in the `python-version` setting in a `pyproject.toml` or `ty.toml` configuration file, `ty` silently accepts it. This is inconsistent with the CLI, which already rejects unsupported versions.

## Expected Behavior

When an unsupported `python-version` value is specified in a configuration file, `ty` should reject it at parse time with a clear error message. The error message should indicate which versions are supported. The supported versions are those returned by `PythonVersion::iter()`.

The deserialization path must validate the version against the supported set. If an unsupported version is encountered, deserialization should return an error in the format:

```
unsupported value `{version}` for `python-version`; expected one of `{list of supported versions}`
```

## What to Look At

Configuration files are parsed using the options metadata layer. The `python-version` field in the environment options is deserialized from TOML configuration. When deserializing, you should check whether the parsed version exists in the set of supported Python versions (from `PythonVersion::iter()`), and return an error if it does not.

The `Options::from_toml_str` method is the entry point for parsing TOML configuration strings, and it accepts a `ValueSource` parameter to indicate where the configuration came from.

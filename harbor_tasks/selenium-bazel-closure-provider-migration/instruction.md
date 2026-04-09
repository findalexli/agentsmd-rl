# Fix Bazel Starlark Provider Access

The `javascript/private/header.bzl` file uses deprecated Bazel provider access patterns that are incompatible with Bazel 7+. The build fails with the legacy struct field access pattern.

## Problem

The file accesses the `closure_js_binary` provider using deprecated Bazel 6.x syntax:
- It uses `getattr(d, "closure_js_binary", None)` to check for provider presence
- It accesses `d.closure_js_binary.bin` to get the binary path

This pattern was removed in Bazel 7. The modern Starlark API requires using the provider symbol directly.

## What You Need to Do

Update `javascript/private/header.bzl` to use the modern Starlark provider API:

1. Load the `ClosureJsBinaryInfo` provider from `@rules_closure//closure/private:defs.bzl`
2. Replace the `getattr(d, "closure_js_binary", None)` check with the modern provider check pattern
3. Replace `d.closure_js_binary.bin` with the modern provider access pattern

The file implements a `_closure_lang_file_impl` function that iterates over `ctx.attr.deps` and extracts binary information from dependencies that have the Closure JS binary provider.

## Key Information

- The `ClosureJsBinaryInfo` provider is defined in `@rules_closure//closure/private:defs.bzl`
- In modern Starlark, providers are checked with `ProviderSymbol in target`
- Provider fields are accessed with `target[ProviderSymbol].field_name`

## Expected Outcome

After the fix, the file should use modern provider patterns that are compatible with Bazel 7+ while maintaining the same functionality of collecting binary paths from dependencies.

# Fix Bazel Starlark Provider Migration for Bazel 7+ Compatibility

The repository uses deprecated Bazel provider access patterns that are incompatible with Bazel 7+. You need to migrate the code to use the modern Starlark provider API.

## Background

In Bazel 6.x and earlier, providers could be accessed via struct field access on targets (e.g., `target.provider_name.field`). In Bazel 7+, providers must be accessed using the modern Starlark provider API:
- Load the provider symbol from its defining module
- Check for provider presence using: `ProviderSymbol in target`
- Access provider fields using: `target[ProviderSymbol].field_name`

## Problem

The file `javascript/private/header.bzl` uses legacy provider access patterns that are deprecated in Bazel 7+:

1. It uses `getattr(d, "closure_js_binary", None)` to check if a target has the Closure JS binary provider (inside the `for d in ctx.attr.deps:` loop)

2. It uses `d.closure_js_binary.bin` to access the `bin` field of the provider

3. It calls `binaries.update({name: d.closure_js_binary.bin})` to store the binary path

These patterns use struct-based provider access which is removed in Bazel 7+.

## Required Migration

Convert the file to use the modern Starlark provider API. The Closure JS binary provider symbol is defined in `@rules_closure//closure/private:defs.bzl`. You must:

1. Load the provider symbol from the rules_closure module

2. Replace the provider presence check with the modern `in` operator pattern

3. Replace the provider field access with modern bracket notation

4. Update the `binaries.update()` call to use bracket notation for the provider field

After your changes, the file must NOT contain any of these deprecated patterns:
- `getattr(d, "closure_js_binary", None)`
- `d.closure_js_binary.bin`

## Verification

After making the changes, the Bazel build should pass:
- `bazel build //javascript/private:all` should succeed
- `bazel build //javascript/private:gen_file` should succeed
- `bazel run //:buildifier -- -mode=check javascript/private/header.bzl` should pass

# Fix Bazel Starlark Provider Migration for Bazel 7+ Compatibility

The repository uses deprecated Bazel provider access patterns that are incompatible with Bazel 7+. You need to migrate the code to use the modern Starlark provider API.

## Background

In Bazel 6.x and earlier, providers could be accessed via struct field access on targets. In Bazel 7+, providers must be accessed using the modern provider symbol API:
- Load the provider symbol from its defining module
- Check for provider presence using: `ProviderSymbol in target`
- Access provider fields using: `target[ProviderSymbol].field_name`

## Required Changes

1. In `javascript/private/header.bzl`, add a load statement to import `ClosureJsBinaryInfo` from `@rules_closure//closure/private:defs.bzl`

2. Find all locations that check for the Closure JS binary provider presence using legacy patterns and replace with the modern `in` check pattern

3. Find all locations that access the `bin` field through legacy struct field access and replace with the modern bracket access pattern

## Specific Requirements

After your changes, the file must contain ALL of the following patterns:

- The load statement: `load("@rules_closure//closure/private:defs.bzl", "ClosureJsBinaryInfo")`
- The provider check pattern: `ClosureJsBinaryInfo in d`
- The provider access pattern: `d[ClosureJsBinaryInfo].bin`
- The binaries.update() call must use: `binaries.update({name: d[ClosureJsBinaryInfo].bin})`

The variable `d` comes from the loop `for d in ctx.attr.deps:`. The provider check must be inside this loop.

The file must NOT contain any of these deprecated patterns:
- `getattr(d, "closure_js_binary", None)`
- `d.closure_js_binary.bin`

## Verification

After making the changes, the Bazel build should pass:
- `bazel build //javascript/private:all` should succeed
- `bazel build //javascript/private:gen_file` should succeed
- `bazel run //:buildifier -- -mode=check javascript/private/header.bzl` should pass

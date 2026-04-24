# Fix JSON Discriminator Extraction Issues in Selenium .NET BiDi

The `GetDiscriminator` extension method in `dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs` has correctness and performance issues when extracting discriminator values from JSON objects.

## Problem Description

When processing JSON objects with nested structures, the discriminator extraction logic incorrectly positions the reader when skipping non-matching properties. The current implementation calls `Skip()` before `Read()` when advancing past property values, which causes the reader to end up in the wrong position. This can cause the parser to miss properties or throw exceptions when dealing with nested objects and arrays.

Additionally, the current approach extracts property names as strings and compares them, which creates unnecessary string allocations.

## Requirements

The `GetDiscriminator` method in `dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs` must meet the following requirements:

1. **Property Name Comparison**: The method must use `Utf8JsonReader.ValueTextEquals()` for comparing property names against the `name` parameter, rather than extracting strings and doing string comparison. This avoids unnecessary string allocations.

2. **Reader Advancement Logic**: When processing properties that don't match the target discriminator name, the method must correctly skip the property value by using the proper `Read()`/`Skip()`/`Read()` sequence. The `Read()` must be called to advance to the property value BEFORE calling `Skip()`, and `Read()` must be called again after `Skip()` to position past the skipped value.

3. **Comments**: The code should include comments explaining the reader advancement operations, particularly why the `Read()` calls are needed around `Skip()`. Follow the commenting style in `dotnet/AGENTS.md`.

4. **Prohibited Patterns**: The implementation must not use `propertyName == name` for comparison or create a `string? propertyName` variable via `GetString()`.

5. **Code Style**: The code must follow the conventions in `dotnet/AGENTS.md`.

## Verification

The project should build successfully after changes:

```bash
bazel build //dotnet/src/webdriver:webdriver
```

Or using dotnet CLI from the `dotnet/` directory.

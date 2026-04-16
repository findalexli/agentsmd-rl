# Fix JSON Discriminator Extraction Issues in Selenium .NET BiDi

The `GetDiscriminator` extension method in `dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs` has correctness and performance issues when extracting discriminator values from JSON objects.

## Problem Description

When processing JSON objects with nested structures, the discriminator extraction logic incorrectly positions the reader when skipping non-matching properties. The current implementation skips to the end of a property value but then advances incorrectly, causing it to miss properties or fail on nested objects and arrays.

Additionally, the current approach creates unnecessary string allocations when comparing property names.

## Requirements

The `GetDiscriminator` method in `dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs` must meet the following requirements:

1. **Property Name Comparison**: The method must use `Utf8JsonReader.ValueTextEquals()` for comparing property names against the `name` parameter, rather than extracting strings and doing string comparison.

2. **Reader Advancement Logic**: When processing properties that don't match the target discriminator name, the method must correctly skip the property value by:
   - Advancing to the property value
   - Skipping the value (which may be a nested object or array)
   - Advancing to the next property or end of object

3. **Required Comments**: The code must contain inline comments explaining the reader advancement operations using these exact phrases:
   - `"move past StartObject to first PropertyName"`
   - `"move to the property value"`
   - `"skip the value (including nested objects/arrays)"`
   - `"move to the next PropertyName or EndObject"`

4. **Prohibited Patterns**: The implementation must NOT contain:
   - The pattern `propertyName == name` for property name comparison
   - The variable assignment pattern `string? propertyName = readerClone.GetString()`

5. **Code Style**: The code must follow the conventions in `dotnet/AGENTS.md`, including that comments should explain *why* operations are performed, not just *what* is happening.

## Verification

The project should build successfully after changes:

```bash
bazel build //dotnet/src/webdriver:webdriver
```

Or using dotnet CLI from the `dotnet/` directory.

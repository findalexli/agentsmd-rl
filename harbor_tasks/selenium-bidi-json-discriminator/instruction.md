# Improve JSON Discriminator Extraction in Selenium .NET BiDi Bindings

The `GetDiscriminator` method in `dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs` has inefficient and potentially buggy JSON parsing logic.

## Problem

The current implementation extracts a discriminator value from a JSON object by iterating through properties. However:

1. **Inefficient property name comparison**: The code converts property names to strings using `GetString()` and then compares, which allocates unnecessary memory.

2. **Incorrect reader advancement**: The logic for advancing the `Utf8JsonReader` through the JSON structure has issues with skipping nested objects and arrays, potentially leading to incorrect discriminator extraction or parsing errors.

## Your Task

Improve the `GetDiscriminator` method to:

1. Use a more efficient method for comparing property names that avoids string allocation
2. Fix the reader advancement logic to correctly handle:
   - Simple property values
   - Nested JSON objects (skip them properly)
   - JSON arrays (skip them properly)
3. Add clear comments explaining each reader movement operation

## Key Method

- File: `dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs`
- Method: `GetDiscriminator` (extension method on `Utf8JsonReader`)

## Requirements

- The method must still correctly extract discriminator values from JSON objects
- The fix should handle edge cases like nested structures
- Comments should explain WHY the reader is being moved, not WHAT is happening
- Follow the code conventions in `dotnet/AGENTS.md`

## Testing

The project should build successfully after your changes:

```bash
bazel build //dotnet/src/webdriver:webdriver
```

Or using dotnet CLI directly from the `dotnet/` directory.

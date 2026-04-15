# Improve JSON Discriminator Extraction in Selenium .NET BiDi Bindings

The Selenium .NET BiDi bindings have a `GetDiscriminator` extension method that extracts discriminator values from JSON objects. This method currently has performance and correctness issues when handling complex JSON structures.

## Problem

When processing JSON objects with nested structures, the discriminator extraction logic fails to correctly skip nested objects and arrays, leading to incorrect reader positioning and potential parsing errors.

Additionally, the current property name comparison approach is inefficient as it involves unnecessary string allocations.

## Your Task

Locate and fix the `GetDiscriminator` extension method that operates on `Utf8JsonReader`. The method should:

1. Use `ValueTextEquals` for property name comparison (comparing the UTF-8 bytes directly without string allocation)
2. Add comments explaining each reader advancement operation using these exact phrases:
   - "move past StartObject to first PropertyName"
   - "move to the property value"
   - "skip the value (including nested objects/arrays)"
   - "move to the next PropertyName or EndObject"
3. Fix the reader advancement logic to correctly handle:
   - Simple property values
   - Nested JSON objects (skip them properly)
   - JSON arrays (skip them properly)

## Requirements

- Remove any usage of `propertyName == name` string comparison pattern
- Remove any usage of `string? propertyName = readerClone.GetString()` variable assignment pattern
- Comments should explain WHY the reader is being moved, not WHAT is happening
- The method must still correctly extract discriminator values from JSON objects
- Follow the code conventions in `dotnet/AGENTS.md`

## Testing

The project should build successfully after your changes:

```bash
bazel build //dotnet/src/webdriver:webdriver
```

Or using dotnet CLI directly from the `dotnet/` directory.

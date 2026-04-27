# Improve JSON Discriminator Extraction in Selenium .NET BiDi

The `GetDiscriminator` extension method in `dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs` needs a performance improvement in how it compares property names during JSON parsing.

## Problem Description

The `GetDiscriminator` method iterates over properties in a JSON object using `Utf8JsonReader` to find and return a discriminator value by name. Currently, the method extracts every property name as a managed `string` (via `GetString()`) and then compares it to the target name using string equality. This creates an unnecessary heap allocation on every loop iteration.

The `Utf8JsonReader` API provides a built-in method for comparing the current token's value directly against a string without allocating a managed string object. The method should use this allocation-free comparison approach instead.

## Requirements

1. **Use allocation-free property name comparison**: Replace the pattern of extracting a property name string and comparing it with the reader's built-in method for checking whether the current property name matches the target name without allocating a string.

2. **Restructure reader advancement for clarity**: Reorganize the `Read()` and `Skip()` calls so that each code path (property match vs. non-match) clearly shows its own sequence of reader operations, rather than sharing an unconditional `Read()` call before the comparison.

3. **Document reader state transitions**: Add inline comments on `Read()` and `Skip()` calls that explain *why* each reader movement is needed (what token the reader is advancing to), following the commenting conventions in `dotnet/AGENTS.md`.

4. **Preserve correctness**: The method must continue to correctly extract discriminator values from JSON objects, including those containing nested objects and arrays as non-target property values.

## Verification

The project should build successfully after changes:

```bash
dotnet build dotnet/src/webdriver/Selenium.WebDriver.csproj
```

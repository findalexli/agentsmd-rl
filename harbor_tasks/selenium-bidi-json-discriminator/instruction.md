# Improve JSON Discriminator Extraction in Selenium .NET BiDi

The `GetDiscriminator` extension method in the .NET BiDi WebDriver source (within the `OpenQA.Selenium.BiDi.Json` namespace, in the file that contains the `JsonExtensions` internal static class) needs a performance improvement in how it compares property names during JSON parsing.

## Problem Description

The `GetDiscriminator` method iterates over properties in a JSON object using `Utf8JsonReader` to find and return a discriminator value by name. Currently, the method extracts every property name as a managed `string` (via `GetString()`), stored in a `string? propertyName` variable, and then compares it to the target name using `==` string equality. This creates an unnecessary heap allocation on every loop iteration.

The `Utf8JsonReader` API provides `ValueTextEquals` for comparing the current token's value directly against a string without allocating a managed string object. The method should use this allocation-free comparison approach instead.

## Requirements

1. **Use allocation-free property name comparison with `ValueTextEquals`**: Replace the pattern of extracting a property name string with `GetString()` and use `ValueTextEquals(name)` to compare the current property name token directly against the target name without allocating a managed string. The `string? propertyName` variable should no longer exist in the method.

2. **Restructure reader advancement for clarity**: Reorganize the `Read()` and `Skip()` calls so that each code path (property match vs. non-match) clearly shows its own sequence of reader operations, rather than sharing an unconditional `Read()` call before the comparison.

3. **Document reader state transitions**: Add inline comments on `Read()` and `Skip()` calls that explain *why* each reader movement is needed (what token the reader is advancing to), following the commenting conventions in `dotnet/AGENTS.md`.

4. **Preserve correctness**: The method must continue to correctly extract discriminator values from JSON objects, including those containing nested objects and arrays as non-target property values.

## Code Style Requirements

The project enforces C# formatting conventions using `dotnet format`. All code must pass:

- `dotnet format style` — file-scoped namespaces, using placement, and other style conventions
- `dotnet format whitespace` — indentation, spacing, and newline conventions

Run `dotnet format` (which combines both style and whitespace checks) to verify compliance.

## Verification

The project should build successfully after changes:

```bash
dotnet build dotnet/src/webdriver/Selenium.WebDriver.csproj
```

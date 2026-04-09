# Task: Optimize BiDi Message Parsing in .NET WebDriver

## Problem

The `ProcessReceivedMessage` method in the BiDi `Broker` class needs optimization. The current implementation uses inefficient string-based JSON property name comparisons and has type inconsistencies when handling parameter indices for BiDi protocol messages.

## Context

The BiDi (Bidirectional) protocol in Selenium WebDriver processes incoming JSON messages from the browser. The message parsing logic needs to be efficient since it handles three message types:
- **Success responses**: Contain `id`, `type: "success"`, and `result`
- **Events**: Contain `type: "event"`, `method`, and `params`
- **Error responses**: Contain `id`, `type: "error"`, `error`, and `message`

## Target

File: `dotnet/src/webdriver/BiDi/Broker.cs`
Function: `ProcessReceivedMessage(byte[] data)`

## Requirements

1. **Optimize property name comparisons**: Replace string-based property name lookups with more efficient UTF-8 byte literal comparisons using `Utf8JsonReader.ValueTextEquals()`

2. **Fix type inconsistencies**: Ensure `paramsStartIndex` and `paramsEndIndex` use consistent integer types that match the `ReadOnlyMemory<byte>` constructor requirements

3. **Improve message type handling**: Convert from string-based type switching to integer constants for better performance

4. **Add robustness**: Handle unknown/unsupported message types gracefully with appropriate logging instead of silently ignoring them

5. **Maintain correctness**: The refactored code must continue to correctly parse all three message types (success, event, error) and extract their respective fields

## Notes

- The BiDi module uses `System.Text.Json` for JSON parsing
- The `Utf8JsonReader` provides `ValueTextEquals(ReadOnlySpan<byte>)` for efficient UTF-8 comparisons
- The method processes raw byte arrays from the WebSocket connection
- Consider the existing logging patterns in the codebase (see other methods in the file for examples)

## Reference

For guidance on coding conventions in this repository:
- See `AGENTS.md` in the repository root for general guidelines
- See `dotnet/AGENTS.md` for .NET-specific conventions including logging, deprecation, async patterns, and XML documentation requirements

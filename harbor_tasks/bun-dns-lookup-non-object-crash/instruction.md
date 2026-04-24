# Bug: `Bun.dns.lookup()` crashes when second argument is a non-object value

## Description

Calling `Bun.dns.lookup()` with a non-object value (such as a string) as the second argument causes a crash instead of gracefully handling the invalid input.

## Reproducer

```js
const dns = Bun.dns;
dns.lookup("127.0.0.1", "cat");
```

This crashes instead of gracefully ignoring the invalid options argument.

## Expected Behavior

When the second argument to `dns.lookup()` is not a valid options object, it should be silently ignored (treated as if no options were provided), and the lookup should proceed normally and return results.

## Files to Investigate

The DNS resolver implementation is in `src/bun.js/api/bun/dns.zig`, specifically in the `Resolver` struct.

## Requirements

1. **Guard the second argument access**: The code must not attempt to access `arguments.ptr[1]` as an object unless it is actually a valid object type. A non-object value (string, number, etc.) passed as options must be silently ignored.

2. **Preserve options parsing**: When a valid object is passed, the code must still extract the `"port"` and `"family"` options using `getTruthy(globalThis, ...)`.

3. **Maintain existing structure**: The `pub const Resolver = struct`, `GetAddrInfo`, and `globalThis` references must remain intact.

## Constraints

- Do not use `std.fs`, `std.posix`, `std.os`, `std.process` where `bun.*` equivalents exist
- Do not use `@import()` inline inside functions; use top-level imports with `const`

## Discovery

To find valid methods for checking object types in Bun's Zig codebase, search under `src/bun.js/` for `fn isXxx` patterns that return `bool`. Methods that return `true` only for objects (not strings, numbers, or other primitives) are suitable.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`

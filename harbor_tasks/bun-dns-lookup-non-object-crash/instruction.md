# Bug: `Bun.dns.lookup()` crashes when second argument is a non-object value

## Description

Calling `Bun.dns.lookup()` with a non-object value (such as a string) as the second argument causes a crash. The DNS resolver in `src/bun.js/api/bun/dns.zig` has a type-checking guard on the second argument that is too permissive — it allows non-object cell values (like strings) through to code that then attempts to read properties from them, triggering a debug assertion failure.

## Reproducer

```js
const dns = Bun.dns;
dns.lookup("127.0.0.1", "cat");
```

This crashes instead of gracefully ignoring the invalid options argument.

## Expected Behavior

When the second argument to `dns.lookup()` is not a valid options object, it should be silently ignored (treated as if no options were provided), and the lookup should proceed normally and return results.

## Files to Investigate

- `src/bun.js/api/bun/dns.zig` — the `Resolver` struct, specifically the argument validation logic around where the second argument is checked before being used as an options object

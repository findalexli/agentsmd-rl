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

The DNS resolver implementation is in `src/bun.js/api/bun/dns.zig`, specifically in the `Resolver` struct. The issue occurs when processing the second argument to the lookup function.

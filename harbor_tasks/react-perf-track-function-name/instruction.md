# Bug: Crash when serializing functions with non-string names

The `addValueToProperties` function in `packages/shared/ReactPerformanceTrackProperties.js` crashes when attempting to describe certain functions that have a non-string `name` property.

## Problem

In JavaScript, accessing `.name` on a function typically returns a string. However, there are edge cases where this is not true:

1. **Classes with static `name` property**: A class can define `static name = <non-string>`, which overrides the default function name behavior.
   ```js
   class Foo {
     static name = {};
   }
   ```

2. **Proxied functions**: When a function is wrapped in a Proxy that intercepts property access, the `.name` property may return something other than a string.

In these cases, the code attempts to concatenate the function name with `"() {}"`, which throws a TypeError when `name` is not a string.

## Expected Behavior

Functions with non-string names should be treated the same as anonymous functions (no name), displaying `() => {}` instead of crashing.

## Files to Modify

- `packages/shared/ReactPerformanceTrackProperties.js`

Look at how the function case is handled in `addValueToProperties` and ensure non-string names are properly type-checked before string concatenation.

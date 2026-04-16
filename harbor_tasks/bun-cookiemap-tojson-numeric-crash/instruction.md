# CookieMap.toJSON() crashes on numeric cookie names

## Bug Description

When a `CookieMap` contains cookies with numeric names (e.g., `"0"`, `"1"`, `"42"`), calling `toJSON()` crashes. The crash does not occur with alphabetic cookie names.

## Expected Behavior

`toJSON()` must complete without crashing regardless of cookie name format, and must return a valid JSON object containing all cookie name-value pairs.

## Requirements

The implementation must:

1. Construct a JavaScript object to hold cookie key-value pairs
2. Iterate over the modified cookies list and insert properties into the JS object
3. Iterate over the original cookies list and insert properties into the JS object, skipping duplicates
4. Use proper JSC exception handling patterns
5. Have at least 8 non-blank lines of actual logic (not be a stub or empty method)

## Implementation Details

The tests verify specific implementation patterns:

- **Property insertion**: The method must use property insertion that handles numeric string keys without crashing. Tests look for method calls on the result object variable and classify them as safe or unsafe based on method name.

- **Key deduplication**: Deduplication must use a native C++ container (such as `HashSet`, `std::set`, `std::unordered_set`, or `WTF::HashSet`) to track seen cookie names, rather than querying the JSObject for property existence. Tests look for declarations of these container types and their `.add()` and `.isNewEntry` usage patterns.

- **Two insertions**: At least two safe property insertions must occur, one per loop.

## Files

- `src/bun.js/bindings/CookieMap.cpp`
- `src/bun.js/bindings/CookieMap.h`

## What to preserve

The fix must not remove or stub out: object construction, exception handling, cookie iteration, or other `CookieMap` methods.
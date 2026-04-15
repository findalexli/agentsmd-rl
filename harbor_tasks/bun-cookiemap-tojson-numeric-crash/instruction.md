# CookieMap.toJSON() crashes with numeric cookie names

## Bug Description

`Bun.CookieMap.toJSON()` crashes with an assertion failure when cookies have numeric names (e.g., `"0"`, `"1"`, `"42"`). The crash occurs in `JSObjectInlines.h` at line 451 in `putDirectInternal`, which asserts `!parseIndex(propertyName)`.

## Reproduction

```js
const map = new Bun.CookieMap("0=first; 1=second; 42=answer");
map.toJSON(); // CRASH: ASSERTION FAILED
```

## Required Fix

The `toJSON` method in `src/bun.js/bindings/CookieMap.cpp` must be modified to:

1. **Fix the property insertion crash**: The method creates a plain JS object and sets properties from cookie names. When a cookie name is a numeric string (like `"0"`, `"1"`, `"42"`), the property insertion path must not trigger the array index assertion. Use a property insertion approach that works correctly for both string keys and numeric string keys.

2. **Fix the deduplication crash**: The method currently checks for existing properties using an approach that also crashes on numeric keys. The deduplication logic must use a different approach that does not query the target object for property existence.

## Constraints

- The fix must still construct a JS object, handle exceptions, and iterate over cookies
- The fix must use proper JSC exception scope patterns (`DECLARE_THROW_SCOPE` or `RELEASE_AND_RETURN`)
- The fix must avoid banned C++ anti-patterns (see the repository's ban-words tests)

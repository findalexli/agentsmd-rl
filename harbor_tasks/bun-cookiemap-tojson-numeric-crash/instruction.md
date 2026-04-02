# CookieMap.toJSON() crashes with numeric cookie names

## Bug Description

`Bun.CookieMap.toJSON()` crashes with an assertion failure when cookies have numeric names (e.g., `"0"`, `"1"`, `"42"`). The crash occurs in the JSC object property insertion path because numeric strings are parsed as array indices, which triggers an assertion in `JSObject::putDirectInternal`.

## Reproduction

```js
const map = new Bun.CookieMap("0=first; 1=second; 42=answer");
map.toJSON(); // CRASH: ASSERTION FAILED: !parseIndex(propertyName)
```

The crash fingerprint points to `JSObjectInlines.h(451)`.

## Relevant Files

- `src/bun.js/bindings/CookieMap.cpp` — the `toJSON` method constructs a plain JS object from cookie entries. The property insertion calls need to handle the case where cookie names are valid array indices.

## Context

Other parts of the Bun codebase that deal with user-controlled property names (FormData, FetchHeaders, environment variables) already handle this correctly. The `toJSON` method needs to follow the same pattern.

Additionally, the current implementation of the deduplication check (skipping original cookies when a modified cookie with the same name exists) could be made more efficient — the current approach queries the object for property existence, but a simpler data structure could avoid the overhead.

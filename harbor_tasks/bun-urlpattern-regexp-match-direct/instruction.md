# Bug: URLPattern internal matching creates excessive GC allocations and pollutes RegExp static properties

## Description

URLPattern's internal matching implementation in `src/bun.js/bindings/webcore/URLPatternComponent.cpp` is inefficient and has a side-effect bug. There are two related problems:

### 1. Excessive GC allocations per match

The current implementation allocates 3 GC objects per URL component match:
- A `RegExpObject` wrapper (created via `RegExpObject::create`)
- A `JSString` for the input
- A result `JSArray` from `exec()`

Since URLPattern matches 8 components (protocol, username, password, hostname, pathname, port, search, hash), this means **24 GC allocations per `test()`/`exec()` call**, plus JS property access to read capture results back from the JSArray.

The `JSC::RegExp` object already holds compiled YARR state and exposes a `match()` method that writes capture offsets directly into an ovector buffer. The intermediate `RegExpObject` wrapper and JS property readback are unnecessary.

Similarly, `matchSpecialSchemeProtocol` creates a new `RegExpObject` for every call and iterates special schemes using `RegExpObject::exec`, when `RegExp::match` would suffice.

### 2. RegExp static property pollution

Because the implementation goes through `RegExpObject::exec()`, each URLPattern match silently mutates the legacy `RegExp.lastMatch` / `RegExp.$1`...`RegExp.$9` static properties. This is observable from user code: calling `pattern.test(url)` leaks internal regex state into these deprecated Annex B properties. The URLPattern spec does not require updating these properties.

### 3. Redundant lock acquisition

`URLPattern::match` in `URLPattern.cpp` acquires `JSLockHolder` separately for each of the 8 component matches (via `componentExec`), when it could acquire the lock once.

## Files to Investigate

- `src/bun.js/bindings/webcore/URLPatternComponent.cpp` — `matchSpecialSchemeProtocol()`, `componentExec()`, `createComponentMatchResult()`
- `src/bun.js/bindings/webcore/URLPatternComponent.h` — method declarations
- `src/bun.js/bindings/webcore/URLPattern.cpp` — `URLPattern::match()` with 8 copy-pasted exec blocks
- `src/bun.js/bindings/webcore/URLPatternConstructorStringParser.cpp` — calls `matchSpecialSchemeProtocol`

## Expected Behavior

- URLPattern matching should use `RegExp::match()` directly with the ovector buffer, avoiding `RegExpObject` creation and JS property readback
- `RegExp.lastMatch` / `RegExp.$N` should not be polluted by URLPattern internals
- The lock should be acquired once per match operation, not per component
- All 408 existing URLPattern tests must continue to pass

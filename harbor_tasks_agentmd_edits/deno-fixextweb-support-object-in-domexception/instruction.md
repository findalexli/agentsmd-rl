# Fix: Support object in DOMException second argument for Node.js compatibility

## Problem

Deno's `DOMException` constructor currently only accepts a string as the second argument for the exception name. However, Node.js also allows passing an options object as the second argument, which can include:
- `name`: The exception name (e.g., "NotFoundError", "AbortError")
- `cause`: The cause of the exception (an Error object or any value)

This incompatibility causes code written for Node.js that uses the options object form to fail or behave incorrectly in Deno:

```javascript
// This works in Node.js but fails/breaks in Deno before the fix
new DOMException("message", { name: "NotFoundError", cause: originalError });
```

## Expected Behavior

The `DOMException` constructor should accept both forms:
1. **Legacy string form** (backwards compatible): `new DOMException("msg", "AbortError")`
2. **Options object form** (Node.js compat): `new DOMException("msg", { name: "AbortError", cause: err })`

When using the options object form:
- The `name` property sets the exception name
- The `cause` property is set as a non-enumerable property on the exception object

## Files to Modify

- `ext/web/01_dom_exception.js` — The DOMException constructor implementation

## Implementation Notes

1. Add `ReflectHas` to the primordials imports (needed to check if `cause` property exists)
2. Change the constructor signature to accept `options` instead of `name`
3. Check if `options` is an object (and not null):
   - If yes: extract `options.name` and check for `options.cause` using `ReflectHas`
   - If `cause` exists, define it as a non-enumerable property using `ObjectDefineProperty`
   - If no: treat it as a string (backwards compatibility)
4. Move the `ReflectConstruct(Error, [], new.target)` call before the name processing to have the error object available for defining the `cause` property

See Node.js implementation for reference:
https://github.com/nodejs/node/blob/9e201e61fd8e4b8bfb74409151cbcbbc7377ca67/lib/internal/per_context/domexception.js#L82-L96

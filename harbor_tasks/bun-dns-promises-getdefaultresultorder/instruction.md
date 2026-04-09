# Expose getDefaultResultOrder on node:dns/promises and fix its return value

## Problem

The `node:dns` module in Bun has two bugs related to `getDefaultResultOrder`:

1. **`dns.getDefaultResultOrder()` returns the wrong value**: Instead of returning a string (`"ipv4first"`, `"ipv6first"`, or `"verbatim"`), it returns the internal `defaultResultOrder` function object itself. This breaks code that expects a string return value, including Vite 8's DNS lookup helper.

2. **`dns.promises.getDefaultResultOrder` is missing**: The function is not exported on the `promises` object, causing `TypeError: promises.getDefaultResultOrder is not a function` when using `import { promises } from "node:dns"`.

3. **`dns.promises.getServers` is also missing**: While fixing the above, `getServers` was also found to be missing from the `promises` export.

### Reproduction

```js
import { promises } from "node:dns";
promises.getDefaultResultOrder();
// TypeError: promises.getDefaultResultOrder is not a function
```

```js
const dns = require("node:dns");
const order = dns.getDefaultResultOrder();
console.log(typeof order);  // "function" (wrong! should be "string")
```

## Expected Behavior

1. `dns.getDefaultResultOrder()` should return a string: `"ipv4first"`, `"ipv6first"`, or `"verbatim"`
2. `dns.promises.getDefaultResultOrder` should be a function that returns the same string
3. `require("node:dns/promises").getDefaultResultOrder` should work
4. `dns.promises.getServers` should be a function returning an array of server strings
5. Calling `setDefaultResultOrder` on either `dns` or `dns.promises` should affect both (shared state)

## Files to Look At

- `src/js/node/dns.ts` — The Node.js DNS compatibility module. Look for:
  - The `getDefaultResultOrder` function (around line 92)
  - The `promises` object export (around line 940+)

## Notes

The fix involves:
1. Changing `return defaultResultOrder;` to `return defaultResultOrder();` in the `getDefaultResultOrder` function
2. Adding `getDefaultResultOrder` and `getServers` to the `promises` object export

Both `setDefaultResultOrder` and the new exports share the same module-level state, so changes via one path are visible via the other (matching Node.js behavior).

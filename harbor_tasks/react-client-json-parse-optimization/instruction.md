# Bug Report: React Flight Client crashes in strict mode when processing server component responses

## Problem

When React's Flight client processes server component responses, it throws a TypeError in strict mode. The issue occurs during JSON parsing of flight protocol messages — specifically, when the response contains model data with lazy/deferred references. Properties defined with `Object.defineProperty` using only a `get` accessor (no `set`) cause failures when the internal walk/revive logic attempts to reassign values on those objects.

Additionally, the current implementation uses `JSON.parse` with a reviver callback, which is measurably slower than parsing the JSON first and then walking the resulting object tree manually. This matters for large server component payloads where parsing performance is critical.

## Expected Behavior

Server component responses should be parsed without errors in strict mode, and the parsing pipeline should efficiently handle large payloads without unnecessary overhead from the reviver-based approach.

## Actual Behavior

A TypeError is thrown when strict mode prevents silent failure of property assignment on getter-only descriptors. The reviver-based JSON parsing also introduces unnecessary performance overhead for every flight response.

## Files to Look At

- `packages/react-client/src/ReactFlightClient.js`
- `packages/react-noop-renderer/src/ReactNoopFlightClient.js`

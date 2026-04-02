# Bug Report: Flow type inconsistencies in React Flight markup client config

## Problem

The React Flight markup client configuration file has type annotation issues that cause Flow type-checking problems. The `resolveServerReference` function accepts a loosely typed parameter where it should use the specific type alias defined in the same file. Additionally, one of the type exports uses an `opaque` modifier inconsistently with how the type is actually used across module boundaries, causing type incompatibilities when other modules attempt to interact with server reference identifiers.

These issues surface when running Flow type checks or when downstream consumers of the markup flight client config try to pass server reference IDs through the expected code paths.

## Expected Behavior

Type exports and function signatures in the markup fork of `ReactFlightClientConfig` should be consistent — type aliases used as function parameters should reference their declared types, and opacity modifiers should only be used where the type genuinely needs to be hidden from external consumers.

## Actual Behavior

A type alias is unnecessarily opaque, and a function parameter uses `mixed` instead of the appropriate specific type, leading to Flow type errors and reduced type safety.

## Files to Look At

- `packages/react-client/src/forks/ReactFlightClientConfig.markup.js`

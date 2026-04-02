# React Flight Debug Channel Variable Bug

## Problem

In the React Flight server rendering package, the `renderToPipeableStream` function in three bundler-specific packages has an incorrect variable check when calling the internal `createRequest` function.

The code appears to be checking if `debugChannel` is defined, but should instead be checking `debugChannelReadable`. This incorrect check causes the server to incorrectly signal that debug info should be emitted even when there is no readable debug channel configured (only a write-only channel). This could cause clients to block forever waiting for debug data that never arrives.

## Affected Packages

Look at the Node.js server implementations in:
- `packages/react-server-dom-esm/src/server/ReactFlightDOMServerNode.js`
- `packages/react-server-dom-parcel/src/server/ReactFlightDOMServerNode.js`
- `packages/react-server-dom-turbopack/src/server/ReactFlightDOMServerNode.js`

## Expected Fix

Compare with the webpack implementation at `packages/react-server-dom-webpack/src/server/ReactFlightDOMServerNode.js`, which uses the correct variable name. Align the ESM, Parcel, and Turbopack implementations to match this pattern.

## Goal

Fix the variable check in the three affected `renderToPipeableStream` functions to use the correct readable channel variable.

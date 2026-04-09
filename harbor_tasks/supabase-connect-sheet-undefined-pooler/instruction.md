# fix(studio): handle undefined connectionStringPooler in connect sheet

## Problem

The ConnectSheet component crashes when `connectionStringPooler` is `undefined`. This happens when the databases query hasn't resolved yet (returns `[]` by default), causing the lookup object to be empty.

The error manifests as: `can't access property "ipv4SupportedForDedicatedPooler", g is undefined`

The crash occurs in the DirectConnectionContent component when trying to access `connectionStringPooler.ipv4SupportedForDedicatedPooler` without null-safety checks.

## Expected Behavior

The connect sheet should render without errors even when the pooler data hasn't loaded yet. The `hasIPv4Addon` boolean should safely default to `false` when `connectionStringPooler` is undefined.

## Files to Look At

- `apps/studio/components/interfaces/ConnectSheet/content/steps/direct-connection/content.tsx` — The DirectConnectionContent component where the crash occurs. Look for how `connectionStringPooler` is accessed and how `hasIPv4Addon` is computed.

## Hints

- Consider what TypeScript type `connectionStringPooler` should have if it can be undefined
- The fix should handle the case where the lookup object access returns undefined
- Default `hasIPv4Addon` to `false` when the pooler is not available

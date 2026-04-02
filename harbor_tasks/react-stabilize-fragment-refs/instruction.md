# Stabilize reactFragments Host Node Handle

## Problem Description

React has an internal handle called `unstable_reactFragments` that is attached to DOM host nodes. This handle was originally introduced for caching Observer instances during experiments and was marked as "unstable" because its stability wasn't yet proven in production.

After extensive testing in production environments, this handle has proven to be stable and should now graduate from the "unstable_" prefix naming convention.

## Files to Modify

1. **packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js**
   - Type definition `InstanceWithFragmentHandles` should use `reactFragments` instead of `unstable_reactFragments`
   - `addFragmentHandleToInstance()` function should read/write to `instance.reactFragments`
   - `deleteChildFromFragmentInstance()` function should check and delete from `instance.reactFragments`

2. **packages/react-native-renderer/src/ReactFiberConfigFabric.js**
   - Type definition `PublicInstanceWithFragmentHandles` should use `reactFragments` instead of `unstable_reactFragments`
   - `addFragmentHandleToInstance()` and `deleteChildFromFragmentInstance()` functions should use the stabilized property name

3. **packages/react-dom/src/__tests__/ReactDOMFragmentRefs-test.js**
   - Update test assertions that check for `unstable_reactFragments` to use the stabilized `reactFragments` property name

## Requirements

- Remove the `unstable_` prefix from all occurrences of `unstable_reactFragments` in the listed files
- Ensure the type annotations reflect the new stable property name
- Update corresponding test assertions to match the new property name
- The change should be consistent across both the DOM bindings (web) and Fabric (React Native) renderer configurations

## Expected Behavior

After stabilization:
- The property `reactFragments` should be attached to DOM host nodes
- Code accessing this property should use `element.reactFragments` instead of `element.unstable_reactFragments`
- Tests should pass with the new stable property name

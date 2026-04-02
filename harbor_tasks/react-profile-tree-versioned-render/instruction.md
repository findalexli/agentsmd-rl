# Bug Report: Profiling commit tree test uses outdated render API helpers

## Problem

The profiling commit tree builder test file (`profilingCommitTreeBuilder-test.js`) uses the deprecated `getLegacyRenderImplementation` and `getModernRenderImplementation` helper functions from the test utilities. These legacy helpers have been replaced across the codebase with the unified `getVersionedRenderImplementation` utility, but this test file was missed during the migration. As a result, the test file maintains two near-identical test cases — one for legacy render and one for `createRoot` — duplicating logic unnecessarily.

## Expected Behavior

The test should use the current versioned render implementation helper (`getVersionedRenderImplementation`) with a single unified test case that automatically adapts to the appropriate React version, consistent with other test files in the devtools package.

## Actual Behavior

The test imports removed/deprecated helpers (`getLegacyRenderImplementation`, `getModernRenderImplementation`), contains duplicated test logic split across two separate test cases with version-gated annotations, and is inconsistent with the rest of the test suite's render patterns.

## Files to Look At

- `packages/react-devtools-shared/src/__tests__/profilingCommitTreeBuilder-test.js`

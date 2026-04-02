# React Script Warning Bug

## Problem

When trusted types integration is enabled in React, rendering `<script>` tags inside React components produces a console warning saying that scripts are blocked from execution. However, this warning is incorrectly triggered for data block scripts (e.g., `<script type="application/json">` or `<script type="application/ld+json">`) which are never executed by browsers anyway.

## Expected Behavior

Data block script tags should not trigger the warning since they cannot execute by design. Only actual JavaScript script tags should warn.

## Where to Look

The warning logic is in the DOM configuration for React Fiber:
- File: `packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js`
- Look for the `createInstance` function and script tag handling

The test file at `packages/react-dom/src/client/__tests__/trustedTypes-test.internal.js` has test cases that demonstrate the expected behavior.

## Context

- This affects the client-side rendering of script tags
- The warning is tied to the `enableTrustedTypesIntegration` flag
- Data block scripts are defined by the HTML spec as scripts with non-JavaScript MIME types

# Don't warn when rendering data block scripts

## Problem

When Trusted Types integration is enabled, React emits a `console.error` warning whenever a `<script>` tag is rendered client-side. This warning fires even for **data block scripts** — script elements with a non-executable `type` like `application/json` or `application/ld+json`. These scripts are never executed by the browser, so the warning is misleading and cannot be resolved by the developer (moving the content to a `<template>` tag would break the intended usage).

For example, rendering `<script type="application/ld+json">{"@context": "https://schema.org"}</script>` incorrectly triggers:

> Encountered a script tag while rendering React component. Scripts inside React components are never executed when rendering on the client. Consider using template tag instead.

## Expected Behavior

React should only warn about script tags that could actually execute JavaScript. Data block scripts (any script with a `type` attribute that is not a JavaScript MIME type and not a special keyword like `module`, `importmap`, or `speculationrules`) should be rendered without a warning.

## Files to Look At

- `packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js` — Contains the `createInstance` function where the script tag warning is issued. The warning condition needs to be updated to distinguish executable scripts from data blocks.

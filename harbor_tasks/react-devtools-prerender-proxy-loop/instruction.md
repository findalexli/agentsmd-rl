# React DevTools causes CPU spike on pages with prerendering speculation rules

## Problem

When a website uses Chrome's Speculation Rules API for prerendering, opening Chrome DevTools causes the React DevTools service worker to spike CPU usage. The browser's task manager shows the React DevTools service worker consuming excessive CPU indefinitely.

The issue occurs because the DevTools proxy content script injects itself during the prerendering phase. Since Chrome fires `pageshow` events even while prerendering, both the prerendered page and the actual page end up fighting for the same extension port connection, creating a ping-pong loop.

## Expected Behavior

The proxy content script should not inject during prerendering. It should defer its connection until the page is actually active — i.e., wait for prerendering to complete before establishing the DevTools proxy connection. The Flow type definitions should also be updated to reflect the `document.prerendering` API.

## Files to Look At

- `packages/react-devtools-extensions/src/contentScripts/proxy.js` — the content script that bridges the page and the DevTools extension
- `flow-typed/environments/dom.js` — Flow type definitions for DOM APIs

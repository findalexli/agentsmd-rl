# React DevTools: High CPU Usage from Service Worker

## Problem

The React DevTools browser extension is causing sustained high CPU usage, particularly visible in Chrome's Task Manager. The issue manifests when users navigate to sites with speculation rules (pre-rendering enabled).

The problem appears to be in the content script proxy that handles communication between the extension and React applications. When a page is being pre-rendered by the browser, the proxy connection seems to be established prematurely, leading to conflicts when the actual page navigation completes.

## Affected File(s)

- `packages/react-devtools-extensions/src/contentScripts/proxy.js`
- `flow-typed/environments/dom.js` (Flow type definitions)

## Expected Behavior

The DevTools extension should only connect to fully loaded pages, not pages that are still in pre-rendering state. The extension port connection should be deferred until the page is actually being displayed to the user.

## Notes

- The browser fires `pageshow` events during pre-rendering in addition to the actual page display
- The extension cannot handle multiple documents being connected to the same extension port simultaneously
- Consider how the extension should behave when a `pageshow` event fires while `document.prerendering` is still true

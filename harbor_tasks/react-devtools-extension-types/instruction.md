# Add Flow Type Annotations to React DevTools Browser Extension

The React DevTools browser extension files (`packages/react-devtools-extensions/src/background/index.js` and `packages/react-devtools-extensions/src/main/index.js`) use untyped JavaScript for the Chrome extension API. The `chrome` global is declared as `any`, and the port objects used for communication between the extension's background script and content scripts have no type annotations.

This causes several problems:
1. No type safety for the extension port API (disconnect, postMessage, onMessage, onDisconnect)
2. A local `ExtensionPort` type definition in `main/index.js` that's incomplete and duplicated
3. No `@flow` annotation in the background script
4. Function parameters like `tabId`, `port`, and `message` are untyped

Add proper Flow type annotations by:
- Defining shared interfaces for the Chrome extension API in `scripts/flow/react-devtools.js`
- Adding `@flow` to the background script
- Replacing the local `ExtensionPort` type with the shared `ExtensionRuntimePort` interface
- Adding type annotations to all function parameters

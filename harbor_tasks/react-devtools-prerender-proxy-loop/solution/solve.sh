#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'document.prerendering' packages/react-devtools-extensions/src/contentScripts/proxy.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/flow-typed/environments/dom.js b/flow-typed/environments/dom.js
index 331e73f89148..0ea2d2730a06 100644
--- a/flow-typed/environments/dom.js
+++ b/flow-typed/environments/dom.js
@@ -1415,6 +1415,8 @@ declare class Document extends Node {
   links: HTMLCollection<HTMLLinkElement>;
   media: string;
   open(url?: string, name?: string, features?: string, replace?: boolean): any;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Web/API/Document/prerendering} */
+  prerendering: boolean;
   readyState: string;
   referrer: string;
   scripts: HTMLCollection<HTMLScriptElement>;
diff --git a/packages/react-devtools-extensions/src/contentScripts/proxy.js b/packages/react-devtools-extensions/src/contentScripts/proxy.js
index a4e7dd68241c..f2b02463600b 100644
--- a/packages/react-devtools-extensions/src/contentScripts/proxy.js
+++ b/packages/react-devtools-extensions/src/contentScripts/proxy.js
@@ -10,7 +10,7 @@

 'use strict';

-function injectProxy({target}: {target: any}) {
+function injectProxy() {
   // Firefox's behaviour for injecting this content script can be unpredictable
   // While navigating the history, some content scripts might not be re-injected and still be alive
   if (!window.__REACT_DEVTOOLS_PROXY_INJECTED__) {
@@ -32,9 +32,23 @@ function injectProxy({target}: {target: any}) {
   }
 }

+function handlePageShow() {
+  if (document.prerendering) {
+    // React DevTools can't handle multiple documents being connected to the same extension port.
+    // However, browsers are firing pageshow events while prerendering (https://issues.chromium.org/issues/489633225).
+    // We need to wait until prerendering is finished before injecting the proxy.
+    // In browsers with pagereveal support, listening to pagereveal would be sufficient.
+    // Waiting for prerenderingchange is a workaround to support browsers that
+    // have speculationrules but not pagereveal.
+    document.addEventListener('prerenderingchange', injectProxy, {once: true});
+  } else {
+    injectProxy();
+  }
+}
+
 window.addEventListener('pagereveal', injectProxy);
 // For backwards compat with browsers not implementing `pagereveal` which is a fairly new event.
-window.addEventListener('pageshow', injectProxy);
+window.addEventListener('pageshow', handlePageShow);

 window.addEventListener('pagehide', function ({target}) {
   if (target !== window.document) {

PATCH

echo "Patch applied successfully."

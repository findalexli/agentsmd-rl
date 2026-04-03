#!/bin/bash
set -euo pipefail

# Check if already applied (look for ExtensionRuntimePort interface)
if grep -q "interface ExtensionRuntimePort" scripts/flow/react-devtools.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-devtools-extensions/src/background/index.js b/packages/react-devtools-extensions/src/background/index.js
index b25eb5303319..0ed719c20b22 100644
--- a/packages/react-devtools-extensions/src/background/index.js
+++ b/packages/react-devtools-extensions/src/background/index.js
@@ -1,4 +1,12 @@
-/* global chrome */
+/**
+ * Copyright (c) Meta Platforms, Inc. and affiliates.
+ *
+ * This source code is licensed under the MIT license found in the
+ * LICENSE file in the root directory of this source tree.
+ *
+ * @flow
+ */
+/* global chrome, ExtensionRuntimePort */

 'use strict';

@@ -12,20 +20,19 @@ import {
   handleFetchResourceContentScriptMessage,
 } from './messageHandlers';

-/*
-  {
-    [tabId]: {
-      extension: ExtensionPort,
-      proxy: ProxyPort,
-      disconnectPipe: Function,
-    },
-    ...
-   }
- */
-const ports = {};
-
-function registerTab(tabId) {
+const ports: {
+  // TODO: Check why we convert tab IDs to strings, and if we can avoid it
+  [tabId: string]: {
+    extension: ExtensionRuntimePort | null,
+    proxy: ExtensionRuntimePort | null,
+    disconnectPipe: Function | null,
+  },
+} = {};
+
+function registerTab(tabId: number) {
+  // $FlowFixMe[incompatible-type]
   if (!ports[tabId]) {
+    // $FlowFixMe[incompatible-type]
     ports[tabId] = {
       extension: null,
       proxy: null,
@@ -34,18 +41,21 @@ function registerTab(tabId) {
   }
 }

-function registerExtensionPort(port, tabId) {
+function registerExtensionPort(port: ExtensionRuntimePort, tabId: number) {
+  // $FlowFixMe[incompatible-type]
   ports[tabId].extension = port;

   port.onDisconnect.addListener(() => {
     // This should delete disconnectPipe from ports dictionary
+    // $FlowFixMe[incompatible-type]
     ports[tabId].disconnectPipe?.();

-    delete ports[tabId].extension;
+    // $FlowFixMe[incompatible-type]
+    ports[tabId].extension = null;
   });
 }

-function registerProxyPort(port, tabId) {
+function registerProxyPort(port: ExtensionRuntimePort, tabId: string) {
   ports[tabId].proxy = port;

   // In case proxy port was disconnected from the other end, from content script
@@ -54,7 +64,7 @@ function registerProxyPort(port, tabId) {
   port.onDisconnect.addListener(() => {
     ports[tabId].disconnectPipe?.();

-    delete ports[tabId].proxy;
+    ports[tabId].proxy = null;
   });
 }

@@ -73,14 +83,22 @@ chrome.runtime.onConnect.addListener(port => {
     // Proxy content script is executed in tab, so it should have it specified.
     const tabId = port.sender.tab.id;

-    if (ports[tabId]?.proxy) {
-      ports[tabId].disconnectPipe?.();
-      ports[tabId].proxy.disconnect();
+    // $FlowFixMe[incompatible-type]
+    const registeredPort = ports[tabId];
+    const proxy = registeredPort?.proxy;
+    if (proxy) {
+      registeredPort.disconnectPipe?.();
+      proxy.disconnect();
     }

     registerTab(tabId);
-    registerProxyPort(port, tabId);
+    registerProxyPort(
+      port,
+      // $FlowFixMe[incompatible-call]
+      tabId,
+    );

+    // $FlowFixMe[incompatible-type]
     if (ports[tabId].extension) {
       connectExtensionAndProxyPorts(
         ports[tabId].extension,
@@ -97,8 +115,13 @@ chrome.runtime.onConnect.addListener(port => {
     const tabId = +port.name;

     registerTab(tabId);
-    registerExtensionPort(port, tabId);
+    registerExtensionPort(
+      port,
+      // $FlowFixMe[incompatible-call]
+      tabId,
+    );

+    // $FlowFixMe[incompatible-type]
     if (ports[tabId].proxy) {
       connectExtensionAndProxyPorts(
         ports[tabId].extension,
@@ -114,26 +137,33 @@ chrome.runtime.onConnect.addListener(port => {
   console.warn(`Unknown port ${port.name} connected`);
 });

-function connectExtensionAndProxyPorts(extensionPort, proxyPort, tabId) {
-  if (!extensionPort) {
+function connectExtensionAndProxyPorts(
+  maybeExtensionPort: ExtensionRuntimePort | null,
+  maybeProxyPort: ExtensionRuntimePort | null,
+  tabId: number,
+) {
+  if (!maybeExtensionPort) {
     throw new Error(
       `Attempted to connect ports, when extension port is not present`,
     );
   }
+  const extensionPort = maybeExtensionPort;

-  if (!proxyPort) {
+  if (!maybeProxyPort) {
     throw new Error(
       `Attempted to connect ports, when proxy port is not present`,
     );
   }
+  const proxyPort = maybeProxyPort;

+  // $FlowFixMe[incompatible-type]
   if (ports[tabId].disconnectPipe) {
     throw new Error(
       `Attempted to connect already connected ports for tab with id ${tabId}`,
     );
   }

-  function extensionPortMessageListener(message) {
+  function extensionPortMessageListener(message: any) {
     try {
       proxyPort.postMessage(message);
     } catch (e) {
@@ -145,7 +175,7 @@ function connectExtensionAndProxyPorts(extensionPort, proxyPort, tabId) {
     }
   }

-  function proxyPortMessageListener(message) {
+  function proxyPortMessageListener(message: any) {
     try {
       extensionPort.postMessage(message);
     } catch (e) {
@@ -164,6 +194,7 @@ function connectExtensionAndProxyPorts(extensionPort, proxyPort, tabId) {
     // We handle disconnect() calls manually, based on each specific case
     // No need to disconnect other port here

+    // $FlowFixMe[incompatible-type]
     delete ports[tabId].disconnectPipe;
   }

diff --git a/packages/react-devtools-extensions/src/main/index.js b/packages/react-devtools-extensions/src/main/index.js
index c12e392881b6..0072b6934585 100644
--- a/packages/react-devtools-extensions/src/main/index.js
+++ b/packages/react-devtools-extensions/src/main/index.js
@@ -1,4 +1,4 @@
-/* global chrome */
+/* global chrome, ExtensionRuntimePort */
 /** @flow */

 import type {RootType} from 'react-dom/src/client/ReactDOMRoot';
@@ -61,7 +61,7 @@ function createBridge() {
     listen(fn) {
       const bridgeListener = (message: Message) => fn(message);
       // Store the reference so that we unsubscribe from the same object.
-      const portOnMessage = ((port: any): ExtensionPort).onMessage;
+      const portOnMessage = port.onMessage;
       portOnMessage.addListener(bridgeListener);

       lastSubscribedBridgeListener = bridgeListener;
@@ -621,22 +621,7 @@ let root: RootType = (null: $FlowFixMe);

 let currentSelectedSource: null | SourceSelection = null;

-type ExtensionEvent = {
-  addListener(callback: (message: Message, port: ExtensionPort) => void): void,
-  removeListener(
-    callback: (message: Message, port: ExtensionPort) => void,
-  ): void,
-};
-
-/** https://developer.chrome.com/docs/extensions/reference/api/runtime#type-Port */
-type ExtensionPort = {
-  onDisconnect: ExtensionEvent,
-  onMessage: ExtensionEvent,
-  postMessage(message: mixed, transferable?: Array<mixed>): void,
-  disconnect(): void,
-};
-
-let port: ExtensionPort = (null: $FlowFixMe);
+let port: ExtensionRuntimePort = (null: $FlowFixMe);

 // In case when multiple navigation events emitted in a short period of time
 // This debounced callback primarily used to avoid mounting React DevTools multiple times, which results
diff --git a/scripts/flow/react-devtools.js b/scripts/flow/react-devtools.js
index 4e0f2a915ede..21f9e441ada6 100644
--- a/scripts/flow/react-devtools.js
+++ b/scripts/flow/react-devtools.js
@@ -17,4 +17,108 @@ declare const __IS_CHROME__: boolean;
 declare const __IS_EDGE__: boolean;
 declare const __IS_NATIVE__: boolean;

-declare const chrome: any;
+interface ExtensionDevtools {
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/devtools/inspectedWindow} */
+  inspectedWindow: $FlowFixMe;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/devtools/network} */
+  network: $FlowFixMe;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/devtools/panels} */
+  panels: $FlowFixMe;
+}
+
+interface ExtensionEvent<Listener: Function> {
+  addListener(callback: Listener): void;
+  removeListener(callback: Listener): void;
+}
+
+/** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/tabs/Tab} */
+// TODO: Only covers used properties. Extend as needed.
+interface ExtensionTab {
+  id?: number;
+}
+
+/** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/MessageSender} */
+// TODO: Only covers used properties. Extend as needed.
+interface ExtensionRuntimeSender {
+  tab?: ExtensionTab;
+}
+
+/** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/Port} */
+// TODO: Only covers used properties. Extend as needed.
+interface ExtensionRuntimePort {
+  disconnect(): void;
+  name: string;
+  onMessage: ExtensionEvent<(message: any, port: ExtensionRuntimePort) => void>;
+  onDisconnect: ExtensionEvent<(port: ExtensionRuntimePort) => void>;
+  postMessage(message: mixed, transferable?: Array<mixed>): void;
+  sender?: ExtensionRuntimeSender;
+}
+
+interface ExtensionMessageSender {
+  id?: string;
+  url?: string;
+  tab?: {
+    id: number,
+    url: string,
+  };
+}
+
+interface ExtensionRuntime {
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/connect} */
+  connect(connectInfo?: {
+    name?: string,
+    includeTlsChannelId?: boolean,
+  }): ExtensionRuntimePort;
+  connect(
+    extensionId: string,
+    connectInfo?: {name?: string, includeTlsChannelId?: boolean},
+  ): ExtensionRuntimePort;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/onMessage} */
+  onMessage: ExtensionEvent<
+    (
+      message: any,
+      sender: ExtensionMessageSender,
+      sendResponse: (response: any) => void,
+    ) => any,
+  >;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/onConnect} */
+  onConnect: ExtensionEvent<(port: ExtensionRuntimePort) => void>;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/sendMessage} */
+  sendMessage(
+    message: any,
+    options?: {includeTlsChannelId?: boolean},
+  ): Promise<any>;
+  sendMessage(
+    extensionId: string,
+    message: any,
+    // We're making this required so that we don't accidentally call the wrong overload.
+    options: {includeTlsChannelId?: boolean},
+  ): Promise<any>;
+}
+
+interface ExtensionTabs {
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/tabs/onActivated} */
+  onActivated: ExtensionEvent<
+    (activeInfo: {
+      previousTabId: number,
+      tabId: number,
+      windowId: number,
+    }) => void,
+  >;
+}
+
+interface ExtensionAPI {
+  devtools: ExtensionDevtools;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/permissions} */
+  permissions: $FlowFixMe;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime} */
+  runtime: ExtensionRuntime;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/scripting} */
+  scripting: $FlowFixMe;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/storage} */
+  storage: $FlowFixMe;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/tabs} */
+  tabs: ExtensionTabs;
+}
+
+declare const chrome: ExtensionAPI;
PATCH

echo "Patch applied successfully."

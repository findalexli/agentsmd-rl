#!/usr/bin/env bash
set -euo pipefail

cd /workspace/electron

# Idempotent: skip if already applied
if grep -q 'lint:api-history' CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index 9189808139478..d41d423002343 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -192,6 +192,7 @@ gh label list --repo electron/electron --search target/ --json name,color --jq '
 ```bash
 npm run lint              # Run all linters
 npm run lint:clang-format # C++ formatting
+npm run lint:api-history  # Validate API history YAML blocks in docs
 ```

 ## Key Files
diff --git a/docs/CLAUDE.md b/docs/CLAUDE.md
new file mode 100644
index 0000000000000..f57dd2d41349f
--- /dev/null
+++ b/docs/CLAUDE.md
@@ -0,0 +1,58 @@
+# Electron Documentation Guide
+
+## API History Migration
+
+Guide: `docs/development/api-history-migration-guide.md`
+Style rules: `docs/development/style-guide.md` (see "API History" section)
+Schema: `docs/api-history.schema.json`
+Lint: `npm run lint:api-history`
+
+### Format
+
+Place YAML history block directly after the Markdown header, before parameters:
+
+````md
+### `module.method(args)`
+
+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/XXXXX
+```
+-->
+
+* `arg` type - Description.
+````
+
+### Finding when an API was added
+
+- `git log --all --reverse --oneline -S "methodName" -- docs/api/file.md` — find first commit adding a method name
+- `git log --reverse -L :FunctionName:path/to/source.cc` — trace C++ implementation history
+- `git log --grep="keyword" --oneline` — find merge commits referencing PRs
+- `gh pr view <number> --repo electron/electron --json baseRefName` — verify PR targets main (not a backport)
+- Always use the main-branch PR URL in history blocks, not backport PRs
+
+### Cross-referencing breaking changes
+
+- Search `docs/breaking-changes.md` for the API name to find deprecations/removals
+- Use `git blame` on the breaking-changes entry to find the associated PR
+- Add `breaking-changes-header` field using the heading ID from breaking-changes.md
+
+### Placement rules
+
+- Only add blocks to actual API entries (methods, events, properties with backtick signatures)
+- Do NOT add blocks to section headers like `## Methods`, `### Instance Methods`, `## Events`
+- Module-level blocks go after the `# moduleName` heading, before the module description quote
+- For changes affecting multiple APIs, add a block under each affected top-level heading (see style guide "Change affecting multiple APIs")
+
+### Key details
+
+- `added` and `deprecated` arrays have `maxItems: 1`; `changes` can have multiple items
+- `changes` entries require a `description` field; `added`/`deprecated` do not
+- Wrap descriptions in double quotes to avoid YAML parsing issues with special characters
+- Early Electron APIs (pre-2015) use merge-commit PRs (e.g., `Merge pull request #534`)
+- Very early APIs (2013-2014, e.g., `ipcMain.on`, `ipcRenderer.send`) predate GitHub PRs — skip history blocks for these
+- When multiple APIs were added in the same PR, they all reference the same PR URL
+- Promisification PRs (e.g., #17355) count as `changes` entries with a description
+  - These PRs are breaking changes and should have their notes as "This method now returns a Promise instead of using a callback function."
+- APIs that were deprecated and then removed from docs don't need history blocks (the removal is in `breaking-changes.md`)
diff --git a/docs/api/global-shortcut.md b/docs/api/global-shortcut.md
index e6111dab43f42..6c25717ad1241 100644
--- a/docs/api/global-shortcut.md
+++ b/docs/api/global-shortcut.md
@@ -55,6 +55,13 @@ The `globalShortcut` module has the following methods:

 ### `globalShortcut.register(accelerator, callback)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/534
+```
+-->
+
 * `accelerator` string - An [accelerator](../tutorial/keyboard-shortcuts.md#accelerators) shortcut.
 * `callback` Function

@@ -77,6 +84,13 @@ the app has been authorized as a [trusted accessibility client](https://develope

 ### `globalShortcut.registerAll(accelerators, callback)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/15542
+```
+-->
+
 * `accelerators` string[] - An array of [accelerator](../tutorial/keyboard-shortcuts.md#accelerators) shortcuts.
 * `callback` Function

@@ -96,6 +110,13 @@ the app has been authorized as a [trusted accessibility client](https://develope

 ### `globalShortcut.isRegistered(accelerator)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/534
+```
+-->
+
 * `accelerator` string - An [accelerator](../tutorial/keyboard-shortcuts.md#accelerators) shortcut.

 Returns `boolean` - Whether this application has registered `accelerator`.
@@ -106,10 +127,24 @@ don't want applications to fight for global shortcuts.

 ### `globalShortcut.unregister(accelerator)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/534
+```
+-->
+
 * `accelerator` string - An [accelerator](../tutorial/keyboard-shortcuts.md#accelerators) shortcut.

 Unregisters the global shortcut of `accelerator`.

 ### `globalShortcut.unregisterAll()`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/534
+```
+-->
+
 Unregisters all of the global shortcuts.
diff --git a/docs/api/image-view.md b/docs/api/image-view.md
index b55711c3a1bbf..80c4c8aea3d27 100644
--- a/docs/api/image-view.md
+++ b/docs/api/image-view.md
@@ -35,6 +35,13 @@ webContentsView.webContents.loadURL('https://electronjs.org')

 ## Class: ImageView extends `View`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/46760
+```
+-->
+
 > A View that displays an image.

 Process: [Main](../glossary.md#main-process)
@@ -49,6 +56,13 @@ Process: [Main](../glossary.md#main-process)

 ### `new ImageView()` _Experimental_

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/46760
+```
+-->
+
 Creates an ImageView.

 ### Instance Methods
@@ -58,6 +72,13 @@ addition to those inherited from [View](view.md):

 #### `image.setImage(image)` _Experimental_

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/46760
+```
+-->
+
 * `image` NativeImage

 Sets the image for this `ImageView`. Note that only image formats supported by
diff --git a/docs/api/in-app-purchase.md b/docs/api/in-app-purchase.md
index 0fed7b8c2c1b6..b14b4ef1ba354 100644
--- a/docs/api/in-app-purchase.md
+++ b/docs/api/in-app-purchase.md
@@ -1,5 +1,12 @@
 # inAppPurchase

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/11292
+```
+-->
+
 > In-app purchases on Mac App Store.

 Process: [Main](../glossary.md#main-process)
@@ -10,6 +17,13 @@ The `inAppPurchase` module emits the following events:

 ### Event: 'transactions-updated'

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/11292
+```
+-->
+
 Returns:

 * `event` Event
@@ -23,6 +37,19 @@ The `inAppPurchase` module has the following methods:

 ### `inAppPurchase.purchaseProduct(productID[, opts])`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/11292
+changes:
+  - pr-url: https://github.com/electron/electron/pull/17355
+    description: "This method now returns a Promise instead of using a callback function."
+    breaking-changes-header: api-changed-callback-based-versions-of-promisified-apis
+  - pr-url: https://github.com/electron/electron/pull/35902
+    description: "Added `username` option to `opts` parameter."
+```
+-->
+
 * `productID` string
 * `opts` Integer | Object (optional) - If specified as an integer, defines the quantity.
   * `quantity` Integer (optional) - The number of items the user wants to purchase.
@@ -34,6 +61,17 @@ You should listen for the `transactions-updated` event as soon as possible and c

 ### `inAppPurchase.getProducts(productIDs)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/12464
+changes:
+  - pr-url: https://github.com/electron/electron/pull/17355
+    description: "This method now returns a Promise instead of using a callback function."
+    breaking-changes-header: api-changed-callback-based-versions-of-promisified-apis
+```
+-->
+
 * `productIDs` string[] - The identifiers of the products to get.

 Returns `Promise<Product[]>` - Resolves with an array of [`Product`](structures/product.md) objects.
@@ -42,24 +80,59 @@ Retrieves the product descriptions.

 ### `inAppPurchase.canMakePayments()`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/11292
+```
+-->
+
 Returns `boolean` - whether a user can make a payment.

 ### `inAppPurchase.restoreCompletedTransactions()`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/21461
+```
+-->
+
 Restores finished transactions. This method can be called either to install purchases on additional devices, or to restore purchases for an application that the user deleted and reinstalled.

 [The payment queue](https://developer.apple.com/documentation/storekit/skpaymentqueue?language=objc) delivers a new transaction for each previously completed transaction that can be restored. Each transaction includes a copy of the original transaction.

 ### `inAppPurchase.getReceiptURL()`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/11292
+```
+-->
+
 Returns `string` - the path to the receipt.

 ### `inAppPurchase.finishAllTransactions()`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/12464
+```
+-->
+
 Completes all pending transactions.

 ### `inAppPurchase.finishTransactionByDate(date)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/12464
+```
+-->
+
 * `date` string - The ISO formatted date of the transaction to finish.

 Completes the pending transactions corresponding to the date.
diff --git a/docs/api/ipc-main.md b/docs/api/ipc-main.md
index b5b84a2176fd5..b14b010f1339a 100644
--- a/docs/api/ipc-main.md
+++ b/docs/api/ipc-main.md
@@ -46,6 +46,13 @@ Listens to `channel`, when a new message arrives `listener` would be called with

 ### `ipcMain.off(channel, listener)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/44651
+```
+-->
+
 * `channel` string
 * `listener` Function
   * `event` [IpcMainEvent][ipc-main-event]
@@ -89,6 +96,13 @@ Removes all listeners from the specified `channel`. Removes all listeners from a

 ### `ipcMain.handle(channel, listener)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/18449
+```
+-->
+
 * `channel` string
 * `listener` Function\<Promise\<any\> | any\>
   * `event` [IpcMainInvokeEvent][ipc-main-invoke-event]
@@ -126,6 +140,13 @@ provided to the renderer process. Please refer to

 ### `ipcMain.handleOnce(channel, listener)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/18449
+```
+-->
+
 * `channel` string
 * `listener` Function\<Promise\<any\> | any\>
   * `event` [IpcMainInvokeEvent][ipc-main-invoke-event]
@@ -136,6 +157,13 @@ Handles a single `invoke`able IPC message, then removes the listener. See

 ### `ipcMain.removeHandler(channel)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/18449
+```
+-->
+
 * `channel` string

 Removes any handler for `channel`, if present.
diff --git a/docs/api/ipc-renderer.md b/docs/api/ipc-renderer.md
index 307ac8bf01263..9438da81268d4 100644
--- a/docs/api/ipc-renderer.md
+++ b/docs/api/ipc-renderer.md
@@ -59,6 +59,13 @@ for more info.

 ### `ipcRenderer.off(channel, listener)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/39816
+```
+-->
+
 * `channel` string
 * `listener` Function
   * `event` [IpcRendererEvent][ipc-renderer-event]
@@ -79,6 +86,13 @@ only the next time a message is sent to `channel`, after which it is removed.

 ### `ipcRenderer.addListener(channel, listener)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/39816
+```
+-->
+
 * `channel` string
 * `listener` Function
   * `event` [IpcRendererEvent][ipc-renderer-event]
@@ -129,6 +143,13 @@ If you want to receive a single response from the main process, like the result

 ### `ipcRenderer.invoke(channel, ...args)`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/18449
+```
+-->
+
 * `channel` string
 * `...args` any[]

@@ -209,6 +230,13 @@ and replies by setting `event.returnValue`.

 ### `ipcRenderer.postMessage(channel, message, [transfer])`

+<!--
+```YAML history
+added:
+  - pr-url: https://github.com/electron/electron/pull/22404
+```
+-->
+
 * `channel` string
 * `message` any
 * `transfer` MessagePort[] (optional)
diff --git a/filenames.auto.gni b/filenames.auto.gni
index 87434e45394cc..47233774a16d0 100644
--- a/filenames.auto.gni
+++ b/filenames.auto.gni
@@ -78,6 +78,7 @@ auto_filenames = {
     "docs/api/web-utils.md",
     "docs/api/webview-tag.md",
     "docs/api/window-open.md",
+    "docs/api/structures/activation-arguments.md",
     "docs/api/structures/base-window-options.md",
     "docs/api/structures/bluetooth-device.md",
     "docs/api/structures/browser-window-options.md",

PATCH

echo "Patch applied successfully."

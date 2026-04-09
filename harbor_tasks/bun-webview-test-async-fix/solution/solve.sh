#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied (check for the FIXED pattern - no double await)
if ! grep -q 'await expect(await view.click' test/js/bun/webview/webview-chrome.test.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply all fixes using sed

# Fix 1: Add isMacOSVersionAtLeast to imports
sed -i 's/import { bunEnv, bunExe, isCI, isMacOS, tempDir } from "harness";/import { bunEnv, bunExe, isCI, isMacOS, isMacOSVersionAtLeast, tempDir } from "harness";/' test/js/bun/webview/webview.test.ts

# Fix 2: Add itRendering helper after 'const it = isMacOS ? test : test.skip;'
sed -i '/const it = isMacOS ? test : test.skip;/a\
// Tests that need frames to tick (rAF / CSS animation). CI macOS runners\
// have no display, so CVDisplayLink never fires and these hang.\
const itRendering = isMacOS ? test.todoIf(isCI) : test.skip;' test/js/bun/webview/webview.test.ts

# Fix 3: Change chrome test - remove double await
sed -i 's/await expect(await view.click(":::invalid"))/await expect(view.click(":::invalid"))/' test/js/bun/webview/webview-chrome.test.ts

# Fix 4-15: itRendering for all rAF-dependent tests
sed -i 's/(isMacOS ? test.todoIf(isCI) : test.skip)("document.visibilityState is visible and rAF fires"/itRendering("document.visibilityState is visible and rAF fires"/' test/js/bun/webview/webview.test.ts
sed -i 's/(isMacOS ? test.todoIf(isCI) : test.skip)("click(selector) waits for actionability/itRendering("click(selector) waits for actionability/' test/js/bun/webview/webview.test.ts
sed -i 's/it.todoIf(isCI)("click(selector) waits for element to appear"/itRendering("click(selector) waits for element to appear"/' test/js/bun/webview/webview.test.ts
sed -i 's/it("click(selector) waits for element to stop animating"/itRendering("click(selector) waits for element to stop animating"/' test/js/bun/webview/webview.test.ts
sed -i 's/it("click(selector) rejects on timeout when obscured"/itRendering("click(selector) rejects on timeout when obscured"/' test/js/bun/webview/webview.test.ts
sed -i 's/it("click(selector) with options"/itRendering("click(selector) with options"/' test/js/bun/webview/webview.test.ts
sed -i 's/it("scrollTo(selector) waits for element to appear"/itRendering("scrollTo(selector) waits for element to appear"/' test/js/bun/webview/webview.test.ts
sed -i 's/it("scrollTo(selector) rejects on timeout"/itRendering("scrollTo(selector) rejects on timeout"/' test/js/bun/webview/webview.test.ts
sed -i 's/it("scroll dispatches native wheel event with isTrusted"/itRendering("scroll dispatches native wheel event with isTrusted"/' test/js/bun/webview/webview.test.ts
sed -i 's/it("scroll: sequential calls in same view"/itRendering("scroll: sequential calls in same view"/' test/js/bun/webview/webview.test.ts
sed -i 's/it("scroll: horizontal"/itRendering("scroll: horizontal"/' test/js/bun/webview/webview.test.ts
sed -i 's/it("scroll: interleaved with click in same view"/itRendering("scroll: interleaved with click in same view"/' test/js/bun/webview/webview.test.ts
sed -i 's/it("scroll: survives navigate (fresh scrolling tree)"/itRendering("scroll: survives navigate (fresh scrolling tree)"/' test/js/bun/webview/webview.test.ts
sed -i 's/it("scroll: targets inner scrollable under view center"/itRendering("scroll: targets inner scrollable under view center"/' test/js/bun/webview/webview.test.ts

# Fix 16-18: closeAll test changes
sed -i 's|await view.navigate("data:text/html,<body>test</body>");|await view.navigate("data:text/html," + encodeURIComponent("<body>test</body>"));|' test/js/bun/webview/webview.test.ts
sed -i 's/stderr: "pipe",/stderr: "inherit",/' test/js/bun/webview/webview.test.ts
sed -i 's/const \[stdout, stderr, exitCode\] = await Promise.all(\[proc.stdout.text(), proc.stderr.text(), proc.exited\]);/const [stdout, exitCode] = await Promise.all([proc.stdout.text(), proc.exited]);/' test/js/bun/webview/webview.test.ts

# Fix 19-20: itPersistentDataStore helper
sed -i '/it("persistent dataStore: localStorage survives across instances"/i\
// _WKWebsiteDataStoreConfiguration initWithDirectory: is macOS 15.2+.\
const itPersistentDataStore = isMacOS \&\& isMacOSVersionAtLeast(15.2) ? test : test.skip;' test/js/bun/webview/webview.test.ts
sed -i 's/it("persistent dataStore: localStorage survives across instances"/itPersistentDataStore("persistent dataStore: localStorage survives across instances"/' test/js/bun/webview/webview.test.ts

echo "Patch applied successfully."

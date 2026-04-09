#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'await expect(view.click' test/js/bun/webview/webview-chrome.test.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the fix for webview test async issues
git apply - <<'PATCH'
diff --git a/test/js/bun/webview/webview-chrome.test.ts b/test/js/bun/webview/webview-chrome.test.ts
index fdeb2f950f2..6d401ece854 100644
--- a/test/js/bun/webview/webview-chrome.test.ts
+++ b/test/js/bun/webview/webview-chrome.test.ts
@@ -665,7 +665,7 @@ it("chrome: click(selector) rejects on invalid selector syntax", async () => {
   await using view = new Bun.WebView({ backend: chrome, width: 200, height: 200 });
   await view.navigate(html("<body></body>"));
   // querySelector throws SyntaxError page-side; the IIFE rejects.
-  await expect(await view.click(":::invalid")).rejects.toThrow();
+  await expect(view.click(":::invalid")).rejects.toThrow();
 });

 // --- Input variants --------------------------------------------------------
diff --git a/test/js/bun/webview/webview.test.ts b/test/js/bun/webview/webview.test.ts
index b000c5c2edd..a422d270303 100644
--- a/test/js/bun/webview/webview.test.ts
+++ b/test/js/bun/webview/webview.test.ts
@@ -1,6 +1,6 @@
 import { dlopen, FFIType, ptr, toArrayBuffer } from "bun:ffi";
 import { expect, test } from "bun:test";
-import { bunEnv, bunExe, isCI, isMacOS, tempDir } from "harness";
+import { bunEnv, bunExe, isCI, isMacOS, isMacOSVersionAtLeast, tempDir } from "harness";

 // FFI shm access for encoding:"shmem" tests. In real use Kitty (or
 // whoever opens the segment) does this — shm_open + mmap + read + unlink.
@@ -49,6 +49,9 @@ function shmRead(name: string, n: number): Buffer {

 // Bun.WebView only exists on darwin for now.
 const it = isMacOS ? test : test.skip;
+// Tests that need frames to tick (rAF / CSS animation). CI macOS runners
+// have no display, so CVDisplayLink never fires and these hang.
+const itRendering = isMacOS ? test.todoIf(isCI) : test.skip;

 // NSURL URLWithString: strictly follows RFC 3986 on x64 macOS system
 // libraries — unencoded <> return nil. arm64 builds of the same OS are
@@ -428,7 +431,7 @@ it("screenshot Blob survives GC (mmap-backed store)", async () => {
 // in the actionability script itself. The -[NSWindow isVisible]→YES override
 // keeps the ActivityState::IsVisible bit set, but CI macOS 14's CVDisplayLink
 // still doesn't callback for the (0,0) alpha=0 window — todo until closed.
-(isMacOS ? test.todoIf(isCI) : test.skip)("document.visibilityState is visible and rAF fires", async () => {
+itRendering("document.visibilityState is visible and rAF fires", async () => {
   await using view = new Bun.WebView({ width: 200, height: 200 });
   await view.navigate(html("<body></body>"));
   const state = await view.evaluate("document.visibilityState");
@@ -467,7 +470,7 @@ it("click dispatches native mousedown/mouseup/click with isTrusted", async () =>
 // TODO: times out on CI (90s) — the rAF-driven actionability poll never
 // resolves. Passes locally; likely a headless/offscreen WKWebView rAF
 // scheduling quirk on the CI runner.
-(isMacOS ? test.todoIf(isCI) : test.skip)("click(selector) waits for actionability, clicks center", async () => {
+itRendering("click(selector) waits for actionability, clicks center", async () => {
   await using view = new Bun.WebView({ width: 300, height: 300 });
   await view.navigate(
     "data:text/html," +
@@ -490,7 +493,7 @@ it("click dispatches native mousedown/mouseup/click with isTrusted", async () =>
   expect(JSON.parse(events)).toEqual([{ trusted: true, x: 90, y: 100, target: "btn" }]);
 });

-it.todoIf(isCI)("click(selector) waits for element to appear", async () => {
+itRendering("click(selector) waits for element to appear", async () => {
   await using view = new Bun.WebView({ width: 300, height: 300 });
   await view.navigate(
     "data:text/html," +
@@ -519,7 +522,7 @@ it.todoIf(isCI)("click(selector) waits for element to appear", async () => {
   expect(await view.evaluate("String(__clicked)")).toBe("1");
 });

-it("click(selector) waits for element to stop animating", async () => {
+itRendering("click(selector) waits for element to stop animating", async () => {
   await using view = new Bun.WebView({ width: 300, height: 300 });
   await view.navigate(
     "data:text/html," +
@@ -539,7 +542,7 @@ it("click(selector) waits for element to stop animating", async () => {
   expect(Number(left)).toBe(100);
 });

-it("click(selector) rejects on timeout when obscured", async () => {
+itRendering("click(selector) rejects on timeout when obscured", async () => {
   await using view = new Bun.WebView({ width: 300, height: 300 });
   await view.navigate(
     "data:text/html," +
@@ -555,7 +558,7 @@ it("click(selector) rejects on timeout when obscured", async () => {
   await expect(view.click("#under", { timeout: 200 })).rejects.toThrow(/timeout waiting for '#under'/);
 });

-it("click(selector) with options", async () => {
+itRendering("click(selector) with options", async () => {
   await using view = new Bun.WebView({ width: 300, height: 300 });
   await view.navigate(
     "data:text/html," +
@@ -611,7 +614,7 @@ it("scrollTo(selector) centers element in viewport", async () => {
   expect(top).toBeLessThan(100);
 });

-it("scrollTo(selector) waits for element to appear", async () => {
+itRendering("scrollTo(selector) waits for element to appear", async () => {
   await using view = new Bun.WebView({ width: 200, height: 200 });
   await view.navigate(
     "data:text/html," +
@@ -657,7 +660,7 @@ it("scrollTo(selector, { block }) controls alignment", async () => {
   expect(topEnd).toBeGreaterThan(140);
 });

-it("scrollTo(selector) rejects on timeout", async () => {
+itRendering("scrollTo(selector) rejects on timeout", async () => {
   await using view = new Bun.WebView({ width: 200, height: 200 });
   await view.navigate(html("<body></body>"));
   await expect(view.scrollTo("#nonexistent", { timeout: 150 })).rejects.toThrow(/timeout waiting for '#nonexistent'/);
@@ -743,7 +746,7 @@ it("press with modifiers fires keydown with modifier flags", async () => {
   expect(JSON.parse(keys)).toEqual([{ key: "Escape", shift: true, meta: false }]);
 });

-it("scroll dispatches native wheel event with isTrusted", async () => {
+itRendering("scroll dispatches native wheel event with isTrusted", async () => {
   await using view = new Bun.WebView({ width: 200, height: 200 });
   await view.navigate(
     "data:text/html," +
@@ -774,7 +777,7 @@ it("scroll dispatches native wheel event with isTrusted", async () => {
   expect(w).toEqual([{ dy: 100, dx: 0, trusted: true, x: 100, y: 100, mode: 0 }]);
 });

-it("scroll: sequential calls in same view", async () => {
+itRendering("scroll: sequential calls in same view", async () => {
   await using view = new Bun.WebView({ width: 200, height: 200 });
   await view.navigate("data:text/html," + encodeURIComponent(`<div style="height:5000px">tall</div>`));
   // Each scroll runs the full double-barrier: both presentation-update
@@ -788,7 +791,7 @@ it("scroll: sequential calls in same view", async () => {
   expect(Number(y)).toBe(120);
 });

-it("scroll: horizontal", async () => {
+itRendering("scroll: horizontal", async () => {
   await using view = new Bun.WebView({ width: 200, height: 200 });
   await view.navigate("data:text/html," + encodeURIComponent(`<div style="width:5000px;height:100px">wide</div>`));
   await view.scroll(80, 0);
@@ -798,7 +801,7 @@ it("scroll: horizontal", async () => {
   expect(Number(x)).toBe(80);
 });

-it("scroll: interleaved with click in same view", async () => {
+itRendering("scroll: interleaved with click in same view", async () => {
   // Scroll uses m_scrollTarget, click uses m_inputTarget — decoupled so a
   // late-firing mouse barrier doesn't clear the scroll barrier's target.
   await using view = new Bun.WebView({ width: 200, height: 200 });
@@ -817,7 +820,7 @@ it("scroll: interleaved with click in same view", async () => {
   expect(JSON.parse(r)).toEqual({ y: 150, c: 2 });
 });

-it("scroll: survives navigate (fresh scrolling tree)", async () => {
+itRendering("scroll: survives navigate (fresh scrolling tree)", async () => {
   // Second navigate gets a fresh scrolling tree. The first presentation-
   // update barrier has to wait for the NEW tree's commit, not a stale one
   // from the previous page.
@@ -831,7 +834,7 @@ it("scroll: survives navigate (fresh scrolling tree)", async () => {
   expect(await view.evaluate("String(scrollY)")).toBe("75");
 });

-it("scroll: targets inner scrollable under view center", async () => {
+itRendering("scroll: targets inner scrollable under view center", async () => {
   // Wheel location is always (W/2, H/2). If a scrollable element covers
   // the center, it receives the wheel and scrolls — the scrolling tree
   // hit-test finds the inner node, not the document root.
@@ -918,7 +921,7 @@ it("WebView.closeAll() kills the host subprocess and pending promises reject",
       "-e",
       `
         const view = new Bun.WebView({ width: 200, height: 200 });
-        await view.navigate("data:text/html,<body>test</body>");
+        await view.navigate("data:text/html," + encodeURIComponent("<body>test</body>"));
         const p = view.evaluate("new Promise(() => {})"); // never resolves
         Bun.WebView.closeAll();
         // SIGKILL → socket EOF or EVFILT_PROC (whichever wins) →
@@ -932,9 +935,9 @@ it("WebView.closeAll() kills the host subprocess and pending promises reject", a
       `,
     ],
     env: bunEnv,
-    stderr: "pipe",
+    stderr: "inherit",
   });
-  const [stdout, stderr, exitCode] = await Promise.all([proc.stdout.text(), proc.stderr.text(), proc.exited]);
+  const [stdout, exitCode] = await Promise.all([proc.stdout.text(), proc.exited]);
   expect(stdout.trim()).toBe("rejected");
   expect(exitCode).toBe(0);
 });
@@ -1020,7 +1023,9 @@ it("process exits after close()", async () => {
   expect(exitCode).toBe(0);
 });

-it("persistent dataStore: localStorage survives across instances", async () => {
+// _WKWebsiteDataStoreConfiguration initWithDirectory: is macOS 15.2+.
+const itPersistentDataStore = isMacOS && isMacOSVersionAtLeast(15.2) ? test : test.skip;
+itPersistentDataStore("persistent dataStore: localStorage survives across instances", async () => {
   using dir = tempDir("webview-persist", {});
   // localStorage needs a real origin; data: URLs are opaque. Use a throwaway server.
   using server = Bun.serve({

PATCH

echo "Patch applied successfully."

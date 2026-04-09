#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if [ -f "test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-a/page.tsx" ]; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/.agents/skills/router-act/SKILL.md b/.agents/skills/router-act/SKILL.md
new file mode 100644
index 0000000000000..6af33a0915238
--- /dev/null
+++ b/.agents/skills/router-act/SKILL.md
@@ -0,0 +1,274 @@
+---
+name: router-act
+description: >
+  How to write end-to-end tests using createRouterAct and LinkAccordion.
+  Use when writing or modifying tests that need to control the timing of
+  internal Next.js requests (like prefetches) or assert on their responses.
+  Covers the act API, fixture patterns, prefetch control via LinkAccordion,
+  fake clocks, and avoiding flaky testing patterns.
+user-invocable: false
+---
+
+# Router Act Testing
+
+Use this skill when writing or modifying tests that involve prefetch requests, client router navigations, or the segment cache. The `createRouterAct` utility from `test/lib/router-act.ts` lets you assert on prefetch and navigation responses in an end-to-end way without coupling to the exact number of requests or the protocol details. This is why most client router-related tests use this pattern.
+
+## When NOT to Use `act`
+
+Don't bother with `act` if you don't need to instrument the network responses — either to control their timing or to assert on what's included in them. If all you're doing is waiting for some part of the UI to appear after a navigation, regular Playwright helpers like `browser.elementById()`, `browser.elementByCss()`, and `browser.waitForElementByCss()` are sufficient.
+
+## Core Principles
+
+1. **Use `LinkAccordion` to control when prefetches happen.** Never let links be visible outside an `act` scope.
+2. **Prefer `'no-requests'`** whenever the data should be served from cache. This is the strongest assertion — it proves the cache is working.
+3. **Avoid retry/polling timers.** The `act` utility exists specifically to replace inherently flaky patterns like `retry()` loops or `setTimeout` waits for network activity. If you find yourself wanting to poll, you're probably not using `act` correctly.
+4. **Avoid the `block` feature.** It's prone to false negatives. Prefer `includes` and `'no-requests'` assertions instead.
+
+## Act API
+
+### Config Options
+
+```typescript
+// Assert NO router requests are made (data served from cache).
+// Prefer this whenever possible — it's the strongest assertion.
+await act(async () => { ... }, 'no-requests')
+
+// Expect at least one response containing this substring
+await act(async () => { ... }, { includes: 'Page content' })
+
+// Expect multiple responses (checked in order)
+await act(async () => { ... }, [
+  { includes: 'First response' },
+  { includes: 'Second response' },
+])
+
+// Assert the same content appears in two separate responses
+await act(async () => { ... }, [
+  { includes: 'Repeated content' },
+  { includes: 'Repeated content' },
+])
+
+// Expect at least one request, don't assert on content
+await act(async () => { ... })
+```
+
+### How `includes` Matching Works
+
+- The `includes` substring is matched against the HTTP response body. Use text content that appears literally in the rendered output (e.g. `'Dynamic content (stale time 60s)'`).
+- Extra responses that don't match any `includes` assertion are silently ignored — you only need to assert on the responses you care about. This keeps tests decoupled from the exact number of requests the router makes.
+- Each `includes` expectation claims exactly one response. If the same substring appears in N separate responses, provide N separate `{ includes: '...' }` entries.
+
+### What `act` Does Internally
+
+`act` intercepts all router requests — prefetches, navigations, and Server Actions — made during the scope:
+
+1. Installs a Playwright route handler to intercept router requests
+2. Runs your scope function
+3. Waits for a `requestIdleCallback` (captures IntersectionObserver-triggered prefetches)
+4. Fulfills buffered responses to the browser
+5. Repeats steps 3-4 until no more requests arrive
+6. Asserts on the responses based on the config
+
+Responses are buffered and only forwarded to the browser after the scope function returns. This means you cannot navigate to a new page and wait for it to render within the same scope — that would deadlock. Trigger the navigation (click the link) and let `act` handle the rest. Read destination page content _after_ `act` returns:
+
+```typescript
+await act(
+  async () => {
+    /* toggle accordion, click link */
+  },
+  { includes: 'Page content' }
+)
+
+// Read content after act returns, not inside the scope
+expect(await browser.elementById('my-content').text()).toBe('Page content')
+```
+
+## LinkAccordion Pattern
+
+### Why LinkAccordion Exists
+
+`LinkAccordion` controls when `<Link>` components enter the DOM. A Next.js `<Link>` triggers a prefetch when it enters the viewport (via IntersectionObserver). By hiding the Link behind a checkbox toggle, you control exactly when prefetches happen — only when you explicitly toggle the accordion inside an `act` scope.
+
+```tsx
+// components/link-accordion.tsx
+'use client'
+import Link from 'next/link'
+import { useState } from 'react'
+
+export function LinkAccordion({ href, children, prefetch }) {
+  const [isVisible, setIsVisible] = useState(false)
+  return (
+    <>
+      <input
+        type="checkbox"
+        checked={isVisible}
+        onChange={() => setIsVisible(!isVisible)}
+        data-link-accordion={href}
+      />
+      {isVisible ? (
+        <Link href={href} prefetch={prefetch}>
+          {children}
+        </Link>
+      ) : (
+        `${children} (link is hidden)`
+      )}
+    </>
+  )
+}
+```
+
+### Standard Navigation Pattern
+
+Always toggle the accordion and click the link inside the same `act` scope:
+
+```typescript
+await act(
+  async () => {
+    // 1. Toggle accordion — Link enters DOM, triggers prefetch
+    const toggle = await browser.elementByCss(
+      'input[data-link-accordion="/target-page"]'
+    )
+    await toggle.click()
+
+    // 2. Click the now-visible link — triggers navigation
+    const link = await browser.elementByCss('a[href="/target-page"]')
+    await link.click()
+  },
+  { includes: 'Expected page content' }
+)
+```
+
+## Common Sources of Flakiness
+
+### Using `browser.back()` with open accordions
+
+Do not use `browser.back()` to return to a page where accordions were previously opened. BFCache restores the full React state including `useState` values, so previously-opened Links are immediately visible. This triggers IntersectionObserver callbacks outside any `act` scope — if the cached data is stale, uncontrolled re-prefetches fire and break subsequent `no-requests` assertions.
+
+The only safe use of `browser.back()`/`browser.forward()` is when testing BFCache behavior specifically.
+
+**Fix:** navigate forward to a fresh hub page instead. See [Hub Pages](#hub-pages).
+
+### Using visible `<Link>` components outside `act` scopes
+
+Any `<Link>` visible in the viewport can trigger a prefetch at any time via IntersectionObserver. If this happens outside an `act` scope, the request is uncontrolled and can interfere with subsequent assertions. Always hide links behind `LinkAccordion` and only toggle them inside `act`.
+
+### Using retry/polling timers to wait for network activity
+
+`retry()`, `setTimeout`, or any polling pattern to wait for prefetches or navigations to settle is inherently flaky. `act` deterministically waits for all router requests to complete before returning.
+
+### Navigating and waiting for render in the same `act` scope
+
+Responses are buffered until the scope exits. Clicking a link then reading destination content in the same scope deadlocks. Read page content after `act` returns instead.
+
+## Hub Pages
+
+When you need to navigate away from a page and come back to test staleness, use "hub" pages instead of `browser.back()`. Each hub is a fresh page with its own `LinkAccordion` components that start closed.
+
+Hub pages use `connection()` to ensure they are dynamically rendered. This guarantees that navigating to a hub always produces a router request, which lets `act` properly manage the navigation and wait for the page to fully render before continuing.
+
+**Hub page pattern:**
+
+```tsx
+// app/my-test/hub-a/page.tsx
+import { Suspense } from 'react'
+import { connection } from 'next/server'
+import { LinkAccordion } from '../../components/link-accordion'
+
+async function Content() {
+  await connection()
+  return <div id="hub-a-content">Hub a</div>
+}
+
+export default function Page() {
+  return (
+    <>
+      <Suspense fallback="Loading...">
+        <Content />
+      </Suspense>
+      <ul>
+        <li>
+          <LinkAccordion href="/my-test/target-page">Target page</LinkAccordion>
+        </li>
+      </ul>
+    </>
+  )
+}
+```
+
+**Target pages link to hubs via LinkAccordion too:**
+
+```tsx
+// On target pages, add LinkAccordion links to hub pages
+<LinkAccordion href="/my-test/hub-a">Hub A</LinkAccordion>
+```
+
+**Test flow:**
+
+```typescript
+// 1. Navigate to target (first visit)
+await act(
+  async () => {
+    /* toggle accordion, click link */
+  },
+  { includes: 'Target content' }
+)
+
+// 2. Navigate to hub-a (fresh page, all accordions closed)
+await act(
+  async () => {
+    const toggle = await browser.elementByCss(
+      'input[data-link-accordion="/my-test/hub-a"]'
+    )
+    await toggle.click()
+    const link = await browser.elementByCss('a[href="/my-test/hub-a"]')
+    await link.click()
+  },
+  { includes: 'Hub a' }
+)
+
+// 3. Advance time
+await page.clock.setFixedTime(startDate + 60 * 1000)
+
+// 4. Navigate back to target from hub (controlled prefetch)
+await act(async () => {
+  const toggle = await browser.elementByCss(
+    'input[data-link-accordion="/my-test/target-page"]'
+  )
+  await toggle.click()
+  const link = await browser.elementByCss('a[href="/my-test/target-page"]')
+  await link.click()
+}, 'no-requests') // or { includes: '...' } if data is stale
+```
+
+## Fake Clock Setup
+
+Segment cache staleness tests use Playwright's clock API to control `Date.now()`:
+
+```typescript
+async function startBrowserWithFakeClock(url: string) {
+  let page!: Playwright.Page
+  const startDate = Date.now()
+
+  const browser = await next.browser(url, {
+    async beforePageLoad(p: Playwright.Page) {
+      page = p
+      await page.clock.install()
+      await page.clock.setFixedTime(startDate)
+    },
+  })
+
+  const act = createRouterAct(page)
+  return { browser, page, act, startDate }
+}
+```
+
+- `setFixedTime` changes `Date.now()` return value but timers still run in real time
+- The segment cache uses `Date.now()` for staleness checks
+- Advancing the clock doesn't trigger IntersectionObserver — only viewport changes do
+- `setFixedTime` does NOT fire pending `setTimeout`/`setInterval` callbacks
+
+## Reference
+
+- `createRouterAct`: `test/lib/router-act.ts`
+- `LinkAccordion`: `test/e2e/app-dir/segment-cache/staleness/components/link-accordion.tsx`
+- Example tests: `test/e2e/app-dir/segment-cache/staleness/`
diff --git a/AGENTS.md b/AGENTS.md
index a58ddfc1df554..64d3c177bdabb 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -407,6 +407,7 @@ Core runtime/bundling rules (always apply; skills above expand on these with ver
 - **`app-page.ts` is a build template compiled by the user's bundler**: Any `require()` in this file is traced by webpack/turbopack at `next build` time. You cannot require internal modules with relative paths because they won't be resolvable from the user's project. Instead, export new helpers from `entry-base.ts` and access them via `entryBase.*` in the template.
 - **Reproducing CI failures locally**: Always match the exact CI env vars (check `pr-status` output for "Job Environment Variables"). Key differences: `IS_WEBPACK_TEST=1` forces webpack (turbopack is default), `NEXT_SKIP_ISOLATE=1` skips packing next.js (hides module resolution failures). Always run without `NEXT_SKIP_ISOLATE` when verifying module resolution fixes.
 - **Showing full stack traces**: Set `__NEXT_SHOW_IGNORE_LISTED=true` to disable the ignore-list filtering in dev server error output. By default, Next.js collapses internal frames to `at ignore-listed frames`, which hides useful context when debugging framework internals. Defined in `packages/next/src/server/patch-error-inspect.ts`.
+- **Router act tests must use LinkAccordion to control prefetches**: Always use `LinkAccordion` to control when prefetches happen inside `act` scopes. Never use `browser.back()` to return to a page where accordion links are already visible — BFCache restores state and triggers uncontrolled re-prefetches. See `$router-act` for full patterns.

 ### Rust/Cargo

diff --git a/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-10/page.tsx b/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-10/page.tsx
index 7bbc8d161ace1..bd4abee68c60b 100644
--- a/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-10/page.tsx
+++ b/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-10/page.tsx
@@ -1,5 +1,6 @@
 import { Suspense } from 'react'
 import { connection } from 'next/server'
+import { LinkAccordion } from '../../../components/link-accordion'

 export const unstable_dynamicStaleTime = 10

@@ -12,8 +13,18 @@ async function Content() {

 export default function Page() {
   return (
-    <Suspense fallback="Loading...">
-      <Content />
-    </Suspense>
+    <>
+      <Suspense fallback="Loading...">
+        <Content />
+      </Suspense>
+      <ul>
+        <li>
+          <LinkAccordion href="/per-page-config/hub-a">Hub A</LinkAccordion>
+        </li>
+        <li>
+          <LinkAccordion href="/per-page-config/hub-b">Hub B</LinkAccordion>
+        </li>
+      </ul>
+    </>
   )
 }
diff --git a/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-60/page.tsx b/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-60/page.tsx
index 11b4b6b837e51..8d06449217360 100644
--- a/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-60/page.tsx
+++ b/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-60/page.tsx
@@ -1,5 +1,6 @@
 import { Suspense } from 'react'
 import { connection } from 'next/server'
+import { LinkAccordion } from '../../../components/link-accordion'

 export const unstable_dynamicStaleTime = 60

@@ -12,8 +13,18 @@ async function Content() {

 export default function Page() {
   return (
-    <Suspense fallback="Loading...">
-      <Content />
-    </Suspense>
+    <>
+      <Suspense fallback="Loading...">
+        <Content />
+      </Suspense>
+      <ul>
+        <li>
+          <LinkAccordion href="/per-page-config/hub-a">Hub A</LinkAccordion>
+        </li>
+        <li>
+          <LinkAccordion href="/per-page-config/hub-c">Hub C</LinkAccordion>
+        </li>
+      </ul>
+    </>
   )
 }
diff --git a/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-a/page.tsx b/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-a/page.tsx
new file mode 100644
index 0000000000000..c11bf5d9d9bf4
--- /dev/null
+++ b/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-a/page.tsx
@@ -0,0 +1,30 @@
+import { Suspense } from 'react'
+import { connection } from 'next/server'
+import { LinkAccordion } from '../../../components/link-accordion'
+
+async function Content() {
+  await connection()
+  return <div id="hub-a-content">Hub a</div>
+}
+
+export default function Page() {
+  return (
+    <>
+      <Suspense fallback="Loading...">
+        <Content />
+      </Suspense>
+      <ul>
+        <li>
+          <LinkAccordion href="/per-page-config/dynamic-stale-10">
+            Dynamic page with stale time of 10 seconds
+          </LinkAccordion>
+        </li>
+        <li>
+          <LinkAccordion href="/per-page-config/dynamic-stale-60">
+            Dynamic page with stale time of 60 seconds
+          </LinkAccordion>
+        </li>
+      </ul>
+    </>
+  )
+}
diff --git a/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-b/page.tsx b/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-b/page.tsx
new file mode 100644
index 0000000000000..800848791f489
--- /dev/null
+++ b/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-b/page.tsx
@@ -0,0 +1,30 @@
+import { Suspense } from 'react'
+import { connection } from 'next/server'
+import { LinkAccordion } from '../../../components/link-accordion'
+
+async function Content() {
+  await connection()
+  return <div id="hub-b-content">Hub b</div>
+}
+
+export default function Page() {
+  return (
+    <>
+      <Suspense fallback="Loading...">
+        <Content />
+      </Suspense>
+      <ul>
+        <li>
+          <LinkAccordion href="/per-page-config/dynamic-stale-10">
+            Dynamic page with stale time of 10 seconds
+          </LinkAccordion>
+        </li>
+        <li>
+          <LinkAccordion href="/per-page-config/dynamic-stale-60">
+            Dynamic page with stale time of 60 seconds
+          </LinkAccordion>
+        </li>
+      </ul>
+    </>
+  )
+}
diff --git a/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-c/page.tsx b/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-c/page.tsx
new file mode 100644
index 0000000000000..2ec4df181f2d5
--- /dev/null
+++ b/test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-c/page.tsx
@@ -0,0 +1,30 @@
+import { Suspense } from 'react'
+import { connection } from 'next/server'
+import { LinkAccordion } from '../../../components/link-accordion'
+
+async function Content() {
+  await connection()
+  return <div id="hub-c-content">Hub c</div>
+}
+
+export default function Page() {
+  return (
+    <>
+      <Suspense fallback="Loading...">
+        <Content />
+      </Suspense>
+      <ul>
+        <li>
+          <LinkAccordion href="/per-page-config/dynamic-stale-10">
+            Dynamic page with stale time of 10 seconds
+          </LinkAccordion>
+        </li>
+        <li>
+          <LinkAccordion href="/per-page-config/dynamic-stale-60">
+            Dynamic page with stale time of 60 seconds
+          </LinkAccordion>
+        </li>
+      </ul>
+    </>
+  )
+}
diff --git a/test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts b/test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts
index 39f3467dcbc6a..3913ce065fa27 100644
--- a/test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts
+++ b/test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts
@@ -217,6 +217,11 @@ describe('segment cache (per-page dynamic stale time)', () => {
     // The global staleTimes.dynamic is 30s. This test verifies that a per-page
     // value of 10s (smaller) causes the data to expire sooner, and a per-page
     // value of 60s (larger) causes the data to last longer.
+    //
+    // Instead of using browser.back() to return to a page that was already
+    // visited, this test navigates forward to fresh "hub" pages. This avoids
+    // flakiness caused by restored accordion state (from BFCache) triggering
+    // uncontrolled re-prefetches outside the act scope.
     const { browser, page, act, startDate } =
       await startBrowserWithFakeClock('/per-page-config')

@@ -235,7 +240,22 @@ describe('segment cache (per-page dynamic stale time)', () => {
       { includes: 'Dynamic content (stale time 10s)' }
     )

-    await browser.back()
+    // Navigate forward to hub/a — a fresh page with its own accordion links.
+    // Because this is a forward navigation to a never-visited page, the
+    // accordions start closed and no uncontrolled prefetches are triggered.
+    await act(
+      async () => {
+        const toggle = await browser.elementByCss(
+          'input[data-link-accordion="/per-page-config/hub-a"]'
+        )
+        await toggle.click()
+        const link = await browser.elementByCss(
+          'a[href="/per-page-config/hub-a"]'
+        )
+        await link.click()
+      },
+      { includes: 'Hub a' }
+    )

     // At 11s the 10s page should be stale, even though the global default
     // is 30s. This proves a smaller per-page value overrides the global.
@@ -243,6 +263,10 @@ describe('segment cache (per-page dynamic stale time)', () => {

     await act(
       async () => {
+        const toggle = await browser.elementByCss(
+          'input[data-link-accordion="/per-page-config/dynamic-stale-10"]'
+        )
+        await toggle.click()
         const link = await browser.elementByCss(
           'a[href="/per-page-config/dynamic-stale-10"]'
         )
@@ -251,7 +275,20 @@ describe('segment cache (per-page dynamic stale time)', () => {
       { includes: 'Dynamic content (stale time 10s)' }
     )

-    await browser.back()
+    // Navigate forward to hub/b
+    await act(
+      async () => {
+        const toggle = await browser.elementByCss(
+          'input[data-link-accordion="/per-page-config/hub-b"]'
+        )
+        await toggle.click()
+        const link = await browser.elementByCss(
+          'a[href="/per-page-config/hub-b"]'
+        )
+        await link.click()
+      },
+      { includes: 'Hub b' }
+    )

     // Now navigate to the 60s page
     await act(
@@ -268,13 +305,30 @@ describe('segment cache (per-page dynamic stale time)', () => {
       { includes: 'Dynamic content (stale time 60s)' }
     )

-    await browser.back()
+    // Navigate forward to hub/c
+    await act(
+      async () => {
+        const toggle = await browser.elementByCss(
+          'input[data-link-accordion="/per-page-config/hub-c"]'
+        )
+        await toggle.click()
+        const link = await browser.elementByCss(
+          'a[href="/per-page-config/hub-c"]'
+        )
+        await link.click()
+      },
+      { includes: 'Hub c' }
+    )

     // At 42s from the 60s page's navigation (11s + 31s), the data should
     // still be fresh — the per-page value of 60s overrides the global 30s.
     await page.clock.setFixedTime(startDate + 42 * 1000)

     await act(async () => {
+      const toggle = await browser.elementByCss(
+        'input[data-link-accordion="/per-page-config/dynamic-stale-60"]'
+      )
+      await toggle.click()
       const link = await browser.elementByCss(
         'a[href="/per-page-config/dynamic-stale-60"]'
       )

PATCH

echo "Patch applied successfully."

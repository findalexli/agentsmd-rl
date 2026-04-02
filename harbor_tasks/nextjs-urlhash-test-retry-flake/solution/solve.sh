#!/usr/bin/env bash
set -euo pipefail

FILE="test/development/pages-dir/client-navigation/url-hash.test.ts"

# Idempotency check: if retry is already imported, patch was already applied
if grep -q "import { retry } from 'next-test-utils'" "$FILE" 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/test/development/pages-dir/client-navigation/url-hash.test.ts b/test/development/pages-dir/client-navigation/url-hash.test.ts
index c821aa555ff1f2..edefe7a8a70657 100644
--- a/test/development/pages-dir/client-navigation/url-hash.test.ts
+++ b/test/development/pages-dir/client-navigation/url-hash.test.ts
@@ -2,6 +2,7 @@

 import path from 'path'
 import { nextTestSetup } from 'e2e-utils'
+import { retry } from 'next-test-utils'

 describe('Client navigation with URL hash', () => {
   const { next } = nextTestSetup({
@@ -31,13 +32,11 @@ describe('Client navigation with URL hash', () => {
       it('should not run getInitialProps', async () => {
         const browser = await next.browser('/nav/hash-changes')

-        const counter = await browser
-          .elementByCss('#via-link')
-          .click()
-          .elementByCss('p')
-          .text()
+        await browser.elementByCss('#via-link').click()

-        expect(counter).toBe('COUNT: 0')
+        await retry(async () => {
+          expect(await browser.elementByCss('p').text()).toBe('COUNT: 0')
+        })

         await browser.close()
       })
@@ -48,41 +47,37 @@ describe('Client navigation with URL hash', () => {
         // Scrolls to item 400 on the page
         await browser.elementByCss('#scroll-to-item-400').click()

-        const scrollPositionBeforeEmptyHash =
-          await browser.eval('window.pageYOffset')
-
-        expect(scrollPositionBeforeEmptyHash).toBe(7258)
+        await retry(async () => {
+          expect(await browser.eval('window.pageYOffset')).toBe(7258)
+        })

         // Scrolls back to top when scrolling to `#` with no value.
         await browser.elementByCss('#via-empty-hash').click()

-        const scrollPositionAfterEmptyHash =
-          await browser.eval('window.pageYOffset')
-
-        expect(scrollPositionAfterEmptyHash).toBe(0)
+        await retry(async () => {
+          expect(await browser.eval('window.pageYOffset')).toBe(0)
+        })

         // Scrolls to item 400 on the page
         await browser.elementByCss('#scroll-to-item-400').click()

-        const scrollPositionBeforeTopHash =
-          await browser.eval('window.pageYOffset')
-
-        expect(scrollPositionBeforeTopHash).toBe(7258)
+        await retry(async () => {
+          expect(await browser.eval('window.pageYOffset')).toBe(7258)
+        })

         // Scrolls back to top when clicking link with href `#top`.
         await browser.elementByCss('#via-top-hash').click()

-        const scrollPositionAfterTopHash =
-          await browser.eval('window.pageYOffset')
-
-        expect(scrollPositionAfterTopHash).toBe(0)
+        await retry(async () => {
+          expect(await browser.eval('window.pageYOffset')).toBe(0)
+        })

         // Scrolls to cjk anchor on the page
         await browser.elementByCss('#scroll-to-cjk-anchor').click()

-        const scrollPositionCJKHash = await browser.eval('window.pageYOffset')
-
-        expect(scrollPositionCJKHash).toBe(17436)
+        await retry(async () => {
+          expect(await browser.eval('window.pageYOffset')).toBe(17436)
+        })
       })

       it('should not scroll to hash when scroll={false} is set', async () => {
@@ -91,9 +86,12 @@ describe('Client navigation with URL hash', () => {
           'document.documentElement.scrollTop'
         )
         await browser.elementByCss('#scroll-to-name-item-400-no-scroll').click()
-        expect(curScroll).toBe(
-          await browser.eval('document.documentElement.scrollTop')
-        )
+
+        await retry(async () => {
+          expect(await browser.eval('document.documentElement.scrollTop')).toBe(
+            curScroll
+          )
+        })
       })

       it('should scroll to the specified position on the same page with a name property', async () => {
@@ -102,17 +100,16 @@ describe('Client navigation with URL hash', () => {
         // Scrolls to item 400 with name="name-item-400" on the page
         await browser.elementByCss('#scroll-to-name-item-400').click()

-        const scrollPosition = await browser.eval('window.pageYOffset')
-
-        expect(scrollPosition).toBe(16258)
+        await retry(async () => {
+          expect(await browser.eval('window.pageYOffset')).toBe(16258)
+        })

         // Scrolls back to top when scrolling to `#` with no value.
         await browser.elementByCss('#via-empty-hash').click()

-        const scrollPositionAfterEmptyHash =
-          await browser.eval('window.pageYOffset')
-
-        expect(scrollPositionAfterEmptyHash).toBe(0)
+        await retry(async () => {
+          expect(await browser.eval('window.pageYOffset')).toBe(0)
+        })
       })

       it('should scroll to the specified position to a new page', async () => {
@@ -124,8 +121,9 @@ describe('Client navigation with URL hash', () => {
           .click()
           .waitForElementByCss('#hash-changes-page')

-        const scrollPosition = await browser.eval('window.pageYOffset')
-        expect(scrollPosition).toBe(7258)
+        await retry(async () => {
+          expect(await browser.eval('window.pageYOffset')).toBe(7258)
+        })
       })

       it('should scroll to the specified CJK position to a new page', async () => {
@@ -137,8 +135,9 @@ describe('Client navigation with URL hash', () => {
           .click()
           .waitForElementByCss('#hash-changes-page')

-        const scrollPosition = await browser.eval('window.pageYOffset')
-        expect(scrollPosition).toBe(17436)
+        await retry(async () => {
+          expect(await browser.eval('window.pageYOffset')).toBe(17436)
+        })
       })

       it('Should update asPath', async () => {
@@ -146,8 +145,11 @@ describe('Client navigation with URL hash', () => {

         await browser.elementByCss('#via-link').click()

-        const asPath = await browser.elementByCss('div#asPath').text()
-        expect(asPath).toBe('ASPATH: /nav/hash-changes#via-link')
+        await retry(async () => {
+          expect(await browser.elementByCss('div#asPath').text()).toBe(
+            'ASPATH: /nav/hash-changes#via-link'
+          )
+        })
       })
     })

@@ -155,13 +157,11 @@ describe('Client navigation with URL hash', () => {
       it('should not run getInitialProps', async () => {
         const browser = await next.browser('/nav/hash-changes')

-        const counter = await browser
-          .elementByCss('#via-a')
-          .click()
-          .elementByCss('p')
-          .text()
+        await browser.elementByCss('#via-a').click()

-        expect(counter).toBe('COUNT: 0')
+        await retry(async () => {
+          expect(await browser.elementByCss('p').text()).toBe('COUNT: 0')
+        })

         await browser.close()
       })
@@ -171,15 +171,15 @@ describe('Client navigation with URL hash', () => {
       it('should not run getInitialProps', async () => {
         const browser = await next.browser('/nav/hash-changes')

-        const counter = await browser
+        await browser
           .elementByCss('#via-a')
           .click()
           .elementByCss('#page-url')
           .click()
-          .elementByCss('p')
-          .text()

-        expect(counter).toBe('COUNT: 1')
+        await retry(async () => {
+          expect(await browser.elementByCss('p').text()).toBe('COUNT: 1')
+        })

         await browser.close()
       })
@@ -187,14 +187,13 @@ describe('Client navigation with URL hash', () => {
       it('should not run getInitialProps when removing via back', async () => {
         const browser = await next.browser('/nav/hash-changes')

-        const counter = await browser
-          .elementByCss('#scroll-to-item-400')
-          .click()
-          .back()
-          .elementByCss('p')
-          .text()
+        await browser.elementByCss('#scroll-to-item-400').click()
+        await browser.back()
+
+        await retry(async () => {
+          expect(await browser.elementByCss('p').text()).toBe('COUNT: 0')
+        })

-        expect(counter).toBe('COUNT: 0')
         await browser.close()
       })
     })
@@ -203,15 +202,15 @@ describe('Client navigation with URL hash', () => {
       it('should not run getInitialProps', async () => {
         const browser = await next.browser('/nav/hash-changes')

-        const counter = await browser
+        await browser
           .elementByCss('#via-a')
           .click()
           .elementByCss('#via-empty-hash')
           .click()
-          .elementByCss('p')
-          .text()

-        expect(counter).toBe('COUNT: 0')
+        await retry(async () => {
+          expect(await browser.elementByCss('p').text()).toBe('COUNT: 0')
+        })

         await browser.close()
       })
@@ -223,15 +222,17 @@ describe('Client navigation with URL hash', () => {
       it('should increment the history state counter', async () => {
         const browser = await next.browser('/nav/hash-changes-with-state#')

-        const historyCount = await browser
+        await browser
           .elementByCss('#increment-history-count')
           .click()
           .elementByCss('#increment-history-count')
           .click()
-          .elementByCss('div#history-count')
-          .text()

-        expect(historyCount).toBe('HISTORY COUNT: 2')
+        await retry(async () => {
+          expect(await browser.elementByCss('div#history-count').text()).toBe(
+            'HISTORY COUNT: 2'
+          )
+        })

         const counter = await browser.elementByCss('p').text()

@@ -244,15 +245,17 @@ describe('Client navigation with URL hash', () => {
       it('should increment the shallow history state counter', async () => {
         const browser = await next.browser('/nav/hash-changes-with-state#')

-        const historyCount = await browser
+        await browser
           .elementByCss('#increment-shallow-history-count')
           .click()
           .elementByCss('#increment-shallow-history-count')
           .click()
-          .elementByCss('div#shallow-history-count')
-          .text()

-        expect(historyCount).toBe('SHALLOW HISTORY COUNT: 2')
+        await retry(async () => {
+          expect(
+            await browser.elementByCss('div#shallow-history-count').text()
+          ).toBe('SHALLOW HISTORY COUNT: 2')
+        })

         const counter = await browser.elementByCss('p').text()

PATCH

echo "Patch applied successfully."

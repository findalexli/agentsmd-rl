#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency check: if timeout: 30000 is already in the test file, skip
if grep -q 'timeout: 30000' test/e2e/app-dir/interoperability-with-pages/navigation.test.ts; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/test/e2e/app-dir/interoperability-with-pages/navigation.test.ts b/test/e2e/app-dir/interoperability-with-pages/navigation.test.ts
index 08f4638a6c519..82010ebe1601d 100644
--- a/test/e2e/app-dir/interoperability-with-pages/navigation.test.ts
+++ b/test/e2e/app-dir/interoperability-with-pages/navigation.test.ts
@@ -20,10 +20,12 @@ describe('navigation between pages and app dir', () => {
   it('It should be able to navigate app -> pages', async () => {
     const browser = await webdriver(next.url, '/app')
     expect(await browser.elementById('app-page').text()).toBe('App Page')
+    // Increased timeout: in dev mode, cross-router navigation triggers on-demand
+    // compilation which can take longer than the default timeout.
     await browser
       .elementById('link-to-pages')
       .click()
-      .waitForElementByCss('#pages-page')
+      .waitForElementByCss('#pages-page', { timeout: 30000 })
     expect(await browser.hasElementByCssSelector('#app-page')).toBeFalse()
     expect(await browser.elementById('pages-page').text()).toBe('Pages Page')
   })
@@ -31,10 +33,12 @@ describe('navigation between pages and app dir', () => {
   it('It should be able to navigate pages -> app', async () => {
     const browser = await webdriver(next.url, '/pages')
     expect(await browser.elementById('pages-page').text()).toBe('Pages Page')
+    // Increased timeout: in dev mode, cross-router navigation triggers on-demand
+    // compilation which can take longer than the default timeout.
     await browser
       .elementById('link-to-app')
       .click()
-      .waitForElementByCss('#app-page')
+      .waitForElementByCss('#app-page', { timeout: 30000 })
     expect(await browser.hasElementByCssSelector('#pages-page')).toBeFalse()
     expect(await browser.elementById('app-page').text()).toBe('App Page')
   })
@@ -43,28 +47,38 @@ describe('navigation between pages and app dir', () => {
   if (!(global as any).isNextDeploy) {
     it('It should be able to navigate pages -> app and go back an forward', async () => {
       const browser = await webdriver(next.url, '/pages')
+      // Increased timeout: in dev mode, cross-router navigation triggers on-demand
+      // compilation which can take longer than the default timeout.
       await browser
         .elementById('link-to-app')
         .click()
-        .waitForElementByCss('#app-page')
-      await browser.back().waitForElementByCss('#pages-page')
+        .waitForElementByCss('#app-page', { timeout: 30000 })
+      await browser
+        .back()
+        .waitForElementByCss('#pages-page', { timeout: 30000 })
       expect(await browser.hasElementByCssSelector('#app-page')).toBeFalse()
       expect(await browser.elementById('pages-page').text()).toBe('Pages Page')
-      await browser.forward().waitForElementByCss('#app-page')
+      await browser
+        .forward()
+        .waitForElementByCss('#app-page', { timeout: 30000 })
       expect(await browser.hasElementByCssSelector('#pages-page')).toBeFalse()
       expect(await browser.elementById('app-page').text()).toBe('App Page')
     })

     it('It should be able to navigate app -> pages and go back and forward', async () => {
       const browser = await webdriver(next.url, '/app')
+      // Increased timeout: in dev mode, cross-router navigation triggers on-demand
+      // compilation which can take longer than the default timeout.
       await browser
         .elementById('link-to-pages')
         .click()
-        .waitForElementByCss('#pages-page')
-      await browser.back().waitForElementByCss('#app-page')
+        .waitForElementByCss('#pages-page', { timeout: 30000 })
+      await browser.back().waitForElementByCss('#app-page', { timeout: 30000 })
       expect(await browser.hasElementByCssSelector('#pages-page')).toBeFalse()
       expect(await browser.elementById('app-page').text()).toBe('App Page')
-      await browser.forward().waitForElementByCss('#pages-page')
+      await browser
+        .forward()
+        .waitForElementByCss('#pages-page', { timeout: 30000 })
       expect(await browser.hasElementByCssSelector('#app-page')).toBeFalse()
       expect(await browser.elementById('pages-page').text()).toBe('Pages Page')
     })

PATCH

echo "Patch applied successfully."

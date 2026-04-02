#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'function calculateUserAgentMetadata' packages/playwright-core/src/server/chromium/crPage.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/playwright-core/src/server/browserContext.ts b/packages/playwright-core/src/server/browserContext.ts
index 19e5a7274ebf0..9233689fe9ca4 100644
--- a/packages/playwright-core/src/server/browserContext.ts
+++ b/packages/playwright-core/src/server/browserContext.ts
@@ -790,74 +790,6 @@ export function normalizeProxySettings(proxy: types.ProxySettings): types.ProxyS
   return { ...proxy, server, bypass };
 }

-// Chromium reference: https://source.chromium.org/chromium/chromium/src/+/main:components/embedder_support/user_agent_utils.cc;l=434
-export function calculateUserAgentEmulation(options: types.BrowserContextOptions): {
-  navigatorPlatform: string | undefined;
-  userAgentMetadata: {
-    mobile: boolean;
-    model: string;
-    architecture: string;
-    platform: string;
-    platformVersion: string;
-  } | undefined;
-} {
-  const ua = options.userAgent;
-  if (!ua)
-    return { navigatorPlatform: undefined, userAgentMetadata: undefined };
-
-  const userAgentMetadata = {
-    mobile: !!options.isMobile,
-    model: '',
-    architecture: 'x86',
-    platform: 'Windows',
-    platformVersion: '',
-  };
-
-  const androidMatch = ua.match(/Android (\d+(\.\d+)?(\.\d+)?)/);
-  const iPhoneMatch = ua.match(/iPhone OS (\d+(_\d+)?)/);
-  const iPadMatch = ua.match(/iPad; CPU OS (\d+(_\d+)?)/);
-  const macOSMatch = ua.match(/Mac OS X (\d+(_\d+)?(_\d+)?)/);
-  const windowsMatch = ua.match(/Windows\D+(\d+(\.\d+)?(\.\d+)?)/);
-  if (androidMatch) {
-    userAgentMetadata.platform = 'Android';
-    userAgentMetadata.platformVersion = androidMatch[1];
-    userAgentMetadata.architecture = 'arm';
-  } else if (iPhoneMatch) {
-    userAgentMetadata.platform = 'iOS';
-    userAgentMetadata.platformVersion = iPhoneMatch[1].replace(/_/g, '.');
-    userAgentMetadata.architecture = 'arm';
-  } else if (iPadMatch) {
-    userAgentMetadata.platform = 'iOS';
-    userAgentMetadata.platformVersion = iPadMatch[1].replace(/_/g, '.');
-    userAgentMetadata.architecture = 'arm';
-  } else if (macOSMatch) {
-    userAgentMetadata.platform = 'macOS';
-    userAgentMetadata.platformVersion = macOSMatch[1].replace(/_/g, '.');
-    if (!ua.includes('Intel'))
-      userAgentMetadata.architecture = 'arm';
-  } else if (windowsMatch) {
-    userAgentMetadata.platform = 'Windows';
-    userAgentMetadata.platformVersion = windowsMatch[1];
-  } else if (ua.toLowerCase().includes('linux')) {
-    userAgentMetadata.platform = 'Linux';
-  }
-  if (ua.includes('ARM') || ua.includes('aarch64'))
-    userAgentMetadata.architecture = 'arm';
-
-  let navigatorPlatform: string | undefined;
-  if (!process.env.PLAYWRIGHT_NO_UA_PLATFORM) {
-    switch (userAgentMetadata.platform) {
-      case 'Android': navigatorPlatform = userAgentMetadata.architecture === 'arm' ? 'Linux armv8l' : 'Linux x86_64'; break;
-      case 'iOS': navigatorPlatform = ua.includes('iPad') ? 'iPad' : 'iPhone'; break;
-      case 'macOS': navigatorPlatform = 'MacIntel'; break;
-      case 'Linux': navigatorPlatform = userAgentMetadata.architecture === 'arm' ? 'Linux aarch64' : 'Linux x86_64'; break;
-      case 'Windows': navigatorPlatform = 'Win32'; break;
-    }
-  }
-
-  return { navigatorPlatform, userAgentMetadata };
-}
-
 const paramsThatAllowContextReuse: (keyof channels.BrowserNewContextForReuseParams)[] = [
   'colorScheme',
   'forcedColors',
diff --git a/packages/playwright-core/src/server/chromium/crPage.ts b/packages/playwright-core/src/server/chromium/crPage.ts
index 91bb36f9fb30b..2891976e9515d 100644
--- a/packages/playwright-core/src/server/chromium/crPage.ts
+++ b/packages/playwright-core/src/server/chromium/crPage.ts
@@ -24,7 +24,6 @@ import * as frames from '../frames';
 import { helper } from '../helper';
 import * as network from '../network';
 import { Page, PageBinding, Worker } from '../page';
-import { calculateUserAgentEmulation } from '../browserContext';
 import { CRBrowserContext } from './crBrowser';
 import { CRCoverage } from './crCoverage';
 import { DragManager } from './crDragDrop';
@@ -986,12 +985,10 @@ class FrameSession {

   async _updateUserAgent(): Promise<void> {
     const options = this._crPage._browserContext._options;
-    const { navigatorPlatform, userAgentMetadata } = calculateUserAgentEmulation(options);
     await this._client.send('Emulation.setUserAgentOverride', {
       userAgent: options.userAgent || '',
       acceptLanguage: options.locale,
-      platform: navigatorPlatform,
-      userAgentMetadata,
+      userAgentMetadata: calculateUserAgentMetadata(options),
     });
   }

@@ -1158,3 +1155,48 @@ async function emulateTimezone(session: CRSession, timezoneId: string) {
     throw exception;
   }
 }
+
+// Chromium reference: https://source.chromium.org/chromium/chromium/src/+/main:components/embedder_support/user_agent_utils.cc;l=434;drc=70a6711e08e9f9e0d8e4c48e9ba5cab62eb010c2
+function calculateUserAgentMetadata(options: types.BrowserContextOptions) {
+  const ua = options.userAgent;
+  if (!ua)
+    return undefined;
+  const metadata: Protocol.Emulation.UserAgentMetadata = {
+    mobile: !!options.isMobile,
+    model: '',
+    architecture: 'x86',
+    platform: 'Windows',
+    platformVersion: '',
+  };
+  const androidMatch = ua.match(/Android (\d+(\.\d+)?(\.\d+)?)/);
+  const iPhoneMatch = ua.match(/iPhone OS (\d+(_\d+)?)/);
+  const iPadMatch = ua.match(/iPad; CPU OS (\d+(_\d+)?)/);
+  const macOSMatch = ua.match(/Mac OS X (\d+(_\d+)?(_\d+)?)/);
+  const windowsMatch = ua.match(/Windows\D+(\d+(\.\d+)?(\.\d+)?)/);
+  if (androidMatch) {
+    metadata.platform = 'Android';
+    metadata.platformVersion = androidMatch[1];
+    metadata.architecture = 'arm';
+  } else if (iPhoneMatch) {
+    metadata.platform = 'iOS';
+    metadata.platformVersion = iPhoneMatch[1];
+    metadata.architecture = 'arm';
+  } else if (iPadMatch) {
+    metadata.platform = 'iOS';
+    metadata.platformVersion = iPadMatch[1];
+    metadata.architecture = 'arm';
+  } else if (macOSMatch) {
+    metadata.platform = 'macOS';
+    metadata.platformVersion = macOSMatch[1];
+    if (!ua.includes('Intel'))
+      metadata.architecture = 'arm';
+  } else if (windowsMatch) {
+    metadata.platform = 'Windows';
+    metadata.platformVersion = windowsMatch[1];
+  } else if (ua.toLowerCase().includes('linux')) {
+    metadata.platform = 'Linux';
+  }
+  if (ua.includes('ARM'))
+    metadata.architecture = 'arm';
+  return metadata;
+}
diff --git a/packages/playwright-core/src/server/firefox/ffBrowser.ts b/packages/playwright-core/src/server/firefox/ffBrowser.ts
index 7c3fb603393a0..4fa67cabc40c9 100644
--- a/packages/playwright-core/src/server/firefox/ffBrowser.ts
+++ b/packages/playwright-core/src/server/firefox/ffBrowser.ts
@@ -17,7 +17,7 @@

 import { assert } from '../../utils';
 import { Browser } from '../browser';
-import { BrowserContext, calculateUserAgentEmulation, verifyGeolocation } from '../browserContext';
+import { BrowserContext, verifyGeolocation } from '../browserContext';
 import * as network from '../network';
 import { ConnectionEvents, FFConnection  } from './ffConnection';
 import { FFPage } from './ffPage';
@@ -189,11 +189,8 @@ export class FFBrowserContext extends BrowserContext {
     promises.push(this.doUpdateDefaultViewport());
     if (this._options.hasTouch)
       promises.push(this._browser.session.send('Browser.setTouchOverride', { browserContextId, hasTouch: true }));
-    if (this._options.userAgent) {
+    if (this._options.userAgent)
       promises.push(this._browser.session.send('Browser.setUserAgentOverride', { browserContextId, userAgent: this._options.userAgent }));
-      const { navigatorPlatform } = calculateUserAgentEmulation(this._options);
-      promises.push(this._browser.session.send('Browser.setPlatformOverride', { browserContextId, platform: navigatorPlatform || null }));
-    }
     if (this._options.bypassCSP)
       promises.push(this._browser.session.send('Browser.setBypassCSP', { browserContextId, bypassCSP: true }));
     if (this._options.ignoreHTTPSErrors || this._options.internalIgnoreHTTPSErrors)
@@ -318,8 +315,6 @@ export class FFBrowserContext extends BrowserContext {

   async setUserAgent(userAgent: string | undefined): Promise<void> {
     await this._browser.session.send('Browser.setUserAgentOverride', { browserContextId: this._browserContextId, userAgent: userAgent || null });
-    const { navigatorPlatform } = calculateUserAgentEmulation({ userAgent });
-    await this._browser.session.send('Browser.setPlatformOverride', { browserContextId: this._browserContextId, platform: navigatorPlatform || null });
   }

   async doUpdateOffline(): Promise<void> {
diff --git a/packages/playwright-core/src/server/webkit/wkPage.ts b/packages/playwright-core/src/server/webkit/wkPage.ts
index 2d042799fada7..76ab0eddec9d1 100644
--- a/packages/playwright-core/src/server/webkit/wkPage.ts
+++ b/packages/playwright-core/src/server/webkit/wkPage.ts
@@ -21,7 +21,6 @@ import { eventsHelper } from '../utils/eventsHelper';
 import { hostPlatform } from '../utils/hostPlatform';
 import { splitErrorMessage } from '../../utils/isomorphic/stackTrace';
 import { PNG, jpegjs } from '../../utilsBundle';
-import { calculateUserAgentEmulation } from '../browserContext';
 import * as dialog from '../dialog';
 import * as dom from '../dom';
 import { TargetClosedError } from '../errors';
@@ -693,8 +692,6 @@ export class WKPage implements PageDelegate {
   async updateUserAgent(): Promise<void> {
     const contextOptions = this._browserContext._options;
     this._updateState('Page.overrideUserAgent', { value: contextOptions.userAgent });
-    const { navigatorPlatform } = calculateUserAgentEmulation(contextOptions);
-    this._updateState('Page.overridePlatform', navigatorPlatform ? { value: navigatorPlatform } : { });
   }

   async bringToFront(): Promise<void> {
diff --git a/tests/library/browsercontext-user-agent.spec.ts b/tests/library/browsercontext-user-agent.spec.ts
index d0fbf2c7e16db..d71399067a55f 100644
--- a/tests/library/browsercontext-user-agent.spec.ts
+++ b/tests/library/browsercontext-user-agent.spec.ts
@@ -107,38 +107,6 @@ it('custom user agent for download', async ({ server, contextFactory, browserVer
   expect(req.headers['user-agent']).toBe('MyCustomUA');
 });

-it('should override navigator.platform to match custom user agent', async ({ browser, server }) => {
-  {
-    const context = await browser.newContext({
-      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
-    });
-    const page = await context.newPage();
-    await page.goto(server.EMPTY_PAGE);
-    expect.soft(await page.evaluate(() => navigator.platform)).toBe('Win32');
-    await context.close();
-  }
-
-  {
-    const context = await browser.newContext({
-      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
-    });
-    const page = await context.newPage();
-    await page.goto(server.EMPTY_PAGE);
-    expect.soft(await page.evaluate(() => navigator.platform)).toBe('MacIntel');
-    await context.close();
-  }
-
-  {
-    const context = await browser.newContext({
-      userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
-    });
-    const page = await context.newPage();
-    await page.goto(server.EMPTY_PAGE);
-    expect.soft(await page.evaluate(() => navigator.platform)).toBe('Linux armv8l');
-    await context.close();
-  }
-});
-
 it('should work for navigator.userAgentData and sec-ch-ua headers', async ({ playwright, browserName, browser, server }) => {
   it.skip(browserName !== 'chromium', 'This API is Chromium-only');

@@ -171,35 +139,6 @@ it('should work for navigator.userAgentData and sec-ch-ua headers', async ({ pla
     expect.soft(await page.evaluate(() => (window.navigator as any).userAgentData.toJSON())).toEqual(
         expect.objectContaining({ mobile: true, platform: 'Android' })
     );
-    expect.soft(await page.evaluate(() => navigator.platform)).toBe('Linux armv8l');
-    await context.close();
-  }
-
-  {
-    const context = await browser.newContext(playwright.devices['Desktop Chrome']);
-    const page = await context.newPage();
-    const [request] = await Promise.all([
-      server.waitForRequest('/empty.html'),
-      page.goto(server.EMPTY_PAGE),
-    ]);
-    expect.soft(request.headers['sec-ch-ua-platform']).toBe(`"Windows"`);
-    expect.soft(await page.evaluate(() => (window.navigator as any).userAgentData.toJSON())).toEqual(
-        expect.objectContaining({ mobile: false, platform: 'Windows' })
-    );
-    expect.soft(await page.evaluate(() => navigator.platform)).toBe('Win32');
-    await context.close();
-  }
-
-  {
-    const context = await browser.newContext({
-      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
-    });
-    const page = await context.newPage();
-    await page.goto(server.EMPTY_PAGE);
-    expect.soft(await page.evaluate(() => (window.navigator as any).userAgentData.toJSON())).toEqual(
-        expect.objectContaining({ platform: 'macOS' })
-    );
-    expect.soft(await page.evaluate(() => navigator.platform)).toBe('MacIntel');
     await context.close();
   }
 });

PATCH

echo "Patch applied successfully."

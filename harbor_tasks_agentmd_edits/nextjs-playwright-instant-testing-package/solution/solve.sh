#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q '"@next/playwright"' packages/next-playwright/package.json 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/next-playwright/README.md b/packages/next-playwright/README.md
new file mode 100644
--- /dev/null
+++ b/packages/next-playwright/README.md
@@ -0,0 +1,107 @@
+# @next/playwright
+
+> - **Status:** Experimental. This API is not yet stable.
+> - **Requires:** [Cache Components](https://nextjs.org/docs) to be enabled.
+
+Playwright helpers for testing Next.js applications.
+
+## Instant Navigation Testing
+
+An **instant navigation** commits immediately without waiting for data fetching.
+The cached shell — including any Suspense loading boundaries — renders right
+away, and dynamic data streams in afterward. The shell is the instant part, not
+the full page.
+
+`instant()` lets you test whether a route achieves this. While the callback is
+active, navigations render only cached and prefetched content. Dynamic data is
+deferred until the callback returns. This lets you make deterministic assertions
+against the shell without race conditions.
+
+The tool assumes a warm cache: all prefetches have completed and all cacheable
+data is available. This way you're testing whether the route is *structured
+correctly* for instant navigation, independent of network timing. If content you
+expected to be cached is missing inside the callback, it points to a problem — a
+missing `use cache` directive, a misplaced Suspense boundary, or a similar gap.
+
+### Examples
+
+**Loading shell appears instantly** (dynamic content behind a Suspense boundary):
+
+```ts
+import { instant } from '@next/playwright'
+
+test('shows loading shell during navigation', async ({ page }) => {
+  await page.goto('/')
+
+  await instant(page, async () => {
+    await page.click('a[href="/dashboard"]')
+
+    // The loading shell is visible — dynamic data is deferred
+    await expect(page.locator('[data-testid="loading"]')).toBeVisible()
+  })
+
+  // After instant() returns, dynamic data streams in normally
+  await expect(page.locator('[data-testid="content"]')).toBeVisible()
+})
+```
+
+**Fully instant navigation** (all content is cached):
+
+```ts
+test('navigates to profile instantly', async ({ page }) => {
+  await page.goto('/')
+
+  await instant(page, async () => {
+    await page.click('a[href="/profile"]')
+
+    // All content renders immediately
+    await expect(page.locator('[data-testid="profile-name"]')).toBeVisible()
+    await expect(page.locator('[data-testid="profile-bio"]')).toBeVisible()
+  })
+})
+```
+
+### Enabling in production builds
+
+In development (`next dev`), the testing API is available by default. In
+production builds, it is disabled unless you explicitly opt in:
+
+```js
+// next.config.js
+module.exports = {
+  experimental: {
+    exposeTestingApiInProductionBuild: true,
+  },
+}
+```
+
+This is not meant to be deployed to live production sites. Only enable it in
+controlled testing environments like preview deployments or CI.
+
+## How it works
+
+`instant()` sets a cookie that tells Next.js to serve only cached data during
+navigations. While the cookie is active:
+
+- **Client-side navigations**: The router renders only what is available in the
+  prefetch cache. Dynamic data is deferred until the cookie is cleared.
+- **Server renders (initial load, reload, MPA navigation)**: The server responds
+  with only the static shell, without any per-request dynamic data.
+
+When the callback completes, the cookie is cleared and normal behavior resumes.
+
+## Design
+
+The layering between this package and Next.js is intentionally very thin. This
+serves as a reference implementation that other testing frameworks and dev tools
+can replicate with minimal effort. The entire mechanism is a single cookie:
+
+```ts
+// Set the cookie to enter instant mode
+document.cookie = 'next-instant-navigation-testing=1; path=/'
+
+// ... run assertions ...
+
+// Clear the cookie to resume normal behavior
+document.cookie = 'next-instant-navigation-testing=; path=/; max-age=0'
+```
diff --git a/packages/next-playwright/package.json b/packages/next-playwright/package.json
new file mode 100644
--- /dev/null
+++ b/packages/next-playwright/package.json
@@ -0,0 +1,24 @@
+{
+  "name": "@next/playwright",
+  "version": "16.2.0-canary.59",
+  "private": true,
+  "repository": {
+    "url": "vercel/next.js",
+    "directory": "packages/next-playwright"
+  },
+  "main": "dist/index.js",
+  "types": "dist/index.d.ts",
+  "files": [
+    "dist"
+  ],
+  "license": "MIT",
+  "scripts": {
+    "build": "node ../../scripts/rm.mjs dist && tsc -d -p tsconfig.json",
+    "prepublishOnly": "cd ../../ && turbo run build",
+    "dev": "tsc -d -w -p tsconfig.json",
+    "typescript": "tsec --noEmit -p tsconfig.json"
+  },
+  "devDependencies": {
+    "typescript": "5.9.2"
+  }
+}
diff --git a/packages/next-playwright/src/index.ts b/packages/next-playwright/src/index.ts
new file mode 100644
--- /dev/null
+++ b/packages/next-playwright/src/index.ts
@@ -0,0 +1,42 @@
+/**
+ * Minimal interface for Playwright's Page. We use a structural type rather than
+ * importing from a specific Playwright package so this works with any version
+ * of playwright, playwright-core, or @playwright/test.
+ */
+interface PlaywrightPage {
+  evaluate<R, Arg>(pageFunction: (arg: Arg) => R, arg: Arg): Promise<R>
+}
+
+const INSTANT_COOKIE = 'next-instant-navigation-testing'
+
+/**
+ * Runs a function with instant navigation enabled. Within this scope,
+ * navigations render the prefetched UI immediately and wait for the
+ * callback to complete before streaming in dynamic data.
+ *
+ * Uses the cookie-based protocol: setting the cookie acquires the
+ * navigation lock (via CookieStore change event), and clearing it
+ * releases the lock.
+ */
+export async function instant<T>(
+  page: PlaywrightPage,
+  fn: () => Promise<T>
+): Promise<T> {
+  // Acquire the lock by setting the cookie from within the page context.
+  // This triggers the CookieStore change event in navigation-testing-lock.ts,
+  // which acquires the in-memory navigation lock.
+  await page.evaluate((name) => {
+    document.cookie = name + '=1; path=/'
+  }, INSTANT_COOKIE)
+  try {
+    return await fn()
+  } finally {
+    // Release the lock by clearing the cookie. For SPA navigations, this
+    // triggers the CookieStore change event which resolves the in-memory
+    // lock. For MPA navigations (reload, plain anchor), the listener in
+    // app-bootstrap.ts triggers a page reload to fetch dynamic data.
+    await page.evaluate((name) => {
+      document.cookie = name + '; path=/; max-age=0'
+    }, INSTANT_COOKIE)
+  }
+}
diff --git a/packages/next-playwright/tsconfig.json b/packages/next-playwright/tsconfig.json
new file mode 100644
--- /dev/null
+++ b/packages/next-playwright/tsconfig.json
@@ -0,0 +1,13 @@
+{
+  "compilerOptions": {
+    "strict": true,
+    "esModuleInterop": true,
+    "target": "es2019",
+    "outDir": "dist",
+    "module": "commonjs",
+    "rootDir": "src",
+    "declaration": true
+  },
+  "include": ["src/**/*.ts"],
+  "exclude": ["node_modules"]
+}
diff --git a/test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts b/test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
index b2b49d0..3309d9c 100644
--- a/test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
+++ b/test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts
@@ -23,6 +23,7 @@
  */

 import { nextTestSetup } from 'e2e-utils'
+import { instant } from '@next/playwright'
 import type * as Playwright from 'playwright'

 describe('instant-navigation-testing-api', () => {
@@ -51,40 +52,6 @@ describe('instant-navigation-testing-api', () => {
     return page!
   }

-  const INSTANT_COOKIE = 'next-instant-navigation-testing'
-
-  /**
-   * Runs a function with instant navigation enabled. Within this scope,
-   * navigations render the prefetched UI immediately and wait for the
-   * callback to complete before streaming in dynamic data.
-   *
-   * Uses the cookie-based protocol: setting the cookie acquires the
-   * navigation lock (via CookieStore change event), and clearing it
-   * releases the lock.
-   */
-  async function instant<T>(
-    page: Playwright.Page,
-    fn: () => Promise<T>
-  ): Promise<T> {
-    // Acquire the lock by setting the cookie from within the page context.
-    // This triggers the CookieStore change event in navigation-testing-lock.ts,
-    // which acquires the in-memory navigation lock.
-    await page.evaluate((name) => {
-      document.cookie = name + '=1; path=/'
-    }, INSTANT_COOKIE)
-    try {
-      return await fn()
-    } finally {
-      // Release the lock by clearing the cookie. For SPA navigations, this
-      // triggers the CookieStore change event which resolves the in-memory
-      // lock. For MPA navigations (reload, plain anchor), the listener in
-      // app-bootstrap.ts triggers a page reload to fetch dynamic data.
-      await page.evaluate((name) => {
-        document.cookie = name + '; path=/; max-age=0'
-      }, INSTANT_COOKIE)
-    }
-  }
-
   it('renders prefetched loading shell instantly during navigation', async () => {
     const page = await openPage('/')

@@ -178,12 +145,10 @@ describe('instant-navigation-testing-api', () => {
     })

     await instant(page, async () => {
-      // Attempt to acquire the lock again by changing the cookie value.
-      // The CookieStore change event fires, and the handler detects that
-      // the lock is already held, logging an error.
-      await page.evaluate((name) => {
-        document.cookie = name + '=nested; path=/'
-      }, INSTANT_COOKIE)
+      // Attempt to acquire the lock again by nesting instant() calls.
+      // The inner call sets the cookie again, and the handler detects
+      // that the lock is already held, logging an error.
+      await instant(page, async () => {})
       const msg = await consolePromise
       expect(msg.text()).toContain('already acquired')
     })
diff --git a/tsconfig.json b/tsconfig.json
index ab578c6..dfd31cb 100644
--- a/tsconfig.json
+++ b/tsconfig.json
@@ -18,7 +18,8 @@
       "e2e-utils/*": ["./test/lib/e2e-utils/*"],
       "test-data-service/*": ["./test/lib/test-data-service/*"],
       "test-log": ["./test/lib/test-log"],
-      "router-act": ["./test/lib/router-act"]
+      "router-act": ["./test/lib/router-act"],
+      "@next/playwright": ["./packages/next-playwright/src/index.ts"]
     }
   },

PATCH

echo "Patch applied successfully."

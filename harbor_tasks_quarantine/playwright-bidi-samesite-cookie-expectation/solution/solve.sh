#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q '|| isBidi) && value === '"'"'None'"'"'' tests/library/browsercontext-fetch.spec.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/tests/bidi/expectations/moz-firefox-nightly-library.txt b/tests/bidi/expectations/moz-firefox-nightly-library.txt
index 5cdceb1d47646..a8c2ce0a3959f 100644
--- a/tests/bidi/expectations/moz-firefox-nightly-library.txt
+++ b/tests/bidi/expectations/moz-firefox-nightly-library.txt
@@ -17,7 +17,6 @@ library/browsercontext-devtools.spec.ts › should close tab via close button [f
 library/browsercontext-devtools.spec.ts › should show no-pages placeholder when all tabs are closed [fail]
 library/browsercontext-devtools.spec.ts › should display screencast image [fail]
 library/browsercontext-events.spec.ts › console event should work with element handles [fail]
-library/browsercontext-fetch.spec.ts › should support set-cookie with SameSite and without Secure attribute over HTTP [fail]
 library/browsercontext-har.spec.ts › should change document URL after redirected navigation [fail]
 library/browsercontext-har.spec.ts › should change document URL after redirected navigation on click [timeout]
 library/browsercontext-har.spec.ts › should goBack to redirected navigation [fail]
diff --git a/tests/library/browsercontext-fetch.spec.ts b/tests/library/browsercontext-fetch.spec.ts
index 8d0457b8a0c25..864f34fa51ac8 100644
--- a/tests/library/browsercontext-fetch.spec.ts
+++ b/tests/library/browsercontext-fetch.spec.ts
@@ -1323,7 +1323,7 @@ it('fetch should not throw on long set-cookie value', async ({ context, server }
   expect(cookies.map(c => c.name)).toContain('bar');
 });

-it('should support set-cookie with SameSite and without Secure attribute over HTTP', async ({ page, server, browserName, isWindows, isLinux, channel }) => {
+it('should support set-cookie with SameSite and without Secure attribute over HTTP', async ({ page, server, browserName, isWindows, isLinux, channel, isBidi }) => {
   for (const value of ['None', 'Lax', 'Strict']) {
     await it.step(`SameSite=${value}`, async () => {
       server.setRoute('/empty.html', (req, res) => {
@@ -1332,7 +1332,7 @@ it('should support set-cookie with SameSite and without Secure attribute over HT
       });
       await page.request.get(server.EMPTY_PAGE);
       const [cookie] = await page.context().cookies();
-      if (browserName === 'chromium' && value === 'None')
+      if ((browserName === 'chromium' || isBidi) && value === 'None')
         expect(cookie).toBeFalsy();
       else if (browserName === 'webkit' && (isLinux || channel === 'webkit-wsl') && value === 'None')
         expect(cookie).toBeFalsy();

PATCH

echo "Patch applied successfully."

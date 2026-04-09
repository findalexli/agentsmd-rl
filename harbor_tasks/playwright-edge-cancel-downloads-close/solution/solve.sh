#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'Ongoing downloads cause crashes in Edge' packages/playwright-core/src/server/chromium/crBrowser.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/playwright-core/src/server/chromium/crBrowser.ts b/packages/playwright-core/src/server/chromium/crBrowser.ts
index b7189d13d73e7..17dc70c9f5975 100644
--- a/packages/playwright-core/src/server/chromium/crBrowser.ts
+++ b/packages/playwright-core/src/server/chromium/crBrowser.ts
@@ -559,6 +559,9 @@ export class CRBrowserContext extends BrowserContext<CREventsMap> {
       return;
     }

+    // Ongoing downloads cause crashes in Edge, so cancel them first.
+    await Promise.all([...this._downloads].map(download => download.cancel().catch(() => {})));
+
     await this._browser._session.send('Target.disposeBrowserContext', { browserContextId: this._browserContextId });
     this._browser._contexts.delete(this._browserContextId);
     for (const [targetId, serviceWorker] of this._browser._serviceWorkers) {
diff --git a/packages/playwright-core/src/server/download.ts b/packages/playwright-core/src/server/download.ts
index 8a88eafcf0114..95ba4eb2b1e1c 100644
--- a/packages/playwright-core/src/server/download.ts
+++ b/packages/playwright-core/src/server/download.ts
@@ -23,23 +23,28 @@ import { Artifact } from './artifact';
 export class Download {
   readonly artifact: Artifact;
   readonly url: string;
+  private _uuid: string;
   private _page: Page;
   private _suggestedFilename: string | undefined;

   constructor(page: Page, downloadsPath: string, uuid: string, url: string, suggestedFilename?: string, downloadFilename?: string) {
     const unaccessibleErrorMessage = page.browserContext._options.acceptDownloads === 'deny' ? 'Pass { acceptDownloads: true } when you are creating your browser context.' : undefined;
     const downloadPath = path.join(downloadsPath, downloadFilename ?? uuid);
-    this.artifact = new Artifact(page, downloadPath, unaccessibleErrorMessage, () => {
-      return this._page.browserContext.cancelDownload(uuid);
-    });
+    this.artifact = new Artifact(page, downloadPath, unaccessibleErrorMessage, () => this.cancel());
     this._page = page;
     this.url = url;
+    this._uuid = uuid;
     this._suggestedFilename = suggestedFilename;
+    // Note: downloads are never removed from the context, so that we can delete them upon context closure.
     page.browserContext._downloads.add(this);
     if (suggestedFilename !== undefined)
       this._fireDownloadEvent();
   }

+  cancel() {
+    return this._page.browserContext.cancelDownload(this._uuid);
+  }
+
   filenameSuggested(suggestedFilename: string) {
     assert(this._suggestedFilename === undefined);
     this._suggestedFilename = suggestedFilename;

PATCH

echo "Patch applied successfully."

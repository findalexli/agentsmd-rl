#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

TARGET="test/integration/next-pages/test/dev-server-puppeteer.ts"

# Idempotency: check if fix already applied
if grep -q 'headless: isMacOS ? "shell" : true' "$TARGET" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/test/integration/next-pages/test/dev-server-puppeteer.ts b/test/integration/next-pages/test/dev-server-puppeteer.ts
index c80ddb7d25c..9d4c0feaa8f 100644
--- a/test/integration/next-pages/test/dev-server-puppeteer.ts
+++ b/test/integration/next-pages/test/dev-server-puppeteer.ts
@@ -18,27 +18,38 @@ if (!browserPath) {
   console.warn("Since a Chromium browser was not found, it will be downloaded by Puppeteer.");
 }

-// On macOS ARM64 CI, Chrome for Testing sometimes fails to launch because
-// macOS quarantines downloaded binaries. Try to remove the quarantine attribute.
+// On macOS CI, Chrome for Testing sometimes fails to launch because
+// macOS quarantines downloaded binaries. Remove the quarantine attribute
+// from all binaries, and also ensure they are executable.
 if (process.platform === "darwin") {
   try {
     const { execSync } = require("child_process");
     const cachePath = join(process.env.HOME || "~", ".cache", "puppeteer");
+    // Remove quarantine from the entire puppeteer cache
     execSync(`xattr -rd com.apple.quarantine "${cachePath}" 2>/dev/null || true`, { stdio: "ignore" });
+    // Also ensure all chrome/chromium binaries in the cache are executable
+    execSync(`find "${cachePath}" -type f -name "Google Chrome for Testing" -exec chmod +x {} + 2>/dev/null || true`, { stdio: "ignore" });
+    execSync(`find "${cachePath}" -type f -name "chrome-headless-shell" -exec chmod +x {} + 2>/dev/null || true`, { stdio: "ignore" });
+    execSync(`find "${cachePath}" -type f -name "chrome" -exec chmod +x {} + 2>/dev/null || true`, { stdio: "ignore" });
   } catch {}
 }

+const isMacOS = process.platform === "darwin";
 const launchOptions: Parameters<typeof launch>[0] = {
-  headless: true,
+  // Use "shell" mode on macOS — it uses chrome-headless-shell which is a
+  // standalone binary that avoids macOS Gatekeeper issues that block the
+  // full Chrome for Testing .app bundle from launching.
+  headless: isMacOS ? "shell" : true,
   dumpio: true,
   // On macOS, pipe mode causes TargetCloseError during browser launch.
-  pipe: process.platform !== "darwin",
-  timeout: 0,
-  protocolTimeout: 0,
+  pipe: !isMacOS,
+  timeout: 30_000,
+  protocolTimeout: 60_000,
   browser: "chrome",
-  // Only pass executablePath if we found a system browser — otherwise let
-  // Puppeteer use its own managed Chrome without interference.
-  ...(browserPath ? { executablePath: browserPath } : {}),
+  // On macOS with "shell" mode, don't pass a system browser path — it would
+  // point to full Chrome, not chrome-headless-shell. On other platforms,
+  // use the system browser if found.
+  ...(!isMacOS && browserPath ? { executablePath: browserPath } : {}),
   args: [
     "--no-sandbox",
     "--disable-setuid-sandbox",
@@ -59,8 +70,8 @@ for (let attempt = 1; attempt <= 3; attempt++) {
   } catch (e: any) {
     console.error(`Browser launch attempt ${attempt}/3 failed: ${e?.message || e}`);
     if (attempt === 3) throw e;
-    // Wait briefly before retrying
-    await new Promise(r => setTimeout(r, 1000));
+    // Give more time between retries (3s) for transient macOS launch issues
+    await new Promise(r => setTimeout(r, 3000));
   }
 }

PATCH

echo "Patch applied successfully."

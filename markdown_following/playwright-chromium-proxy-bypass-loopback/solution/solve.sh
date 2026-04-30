#!/bin/bash
set -euo pipefail

cd /workspace/playwright

TARGET="packages/playwright-core/src/server/chromium/chromium.ts"

# Idempotency guard — skip if patch already applied.
if grep -q 'bypassesLoopback' "${TARGET}"; then
  echo "Patch already applied; skipping."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/playwright-core/src/server/chromium/chromium.ts b/packages/playwright-core/src/server/chromium/chromium.ts
--- a/packages/playwright-core/src/server/chromium/chromium.ts
+++ b/packages/playwright-core/src/server/chromium/chromium.ts
@@ -349,7 +349,8 @@ export class Chromium extends BrowserType {
         proxyBypassRules.push('<-loopback>');
       if (proxy.bypass)
         proxyBypassRules.push(...proxy.bypass.split(',').map(t => t.trim()).map(t => t.startsWith('.') ? '*' + t : t));
-      if (!process.env.PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK && !proxyBypassRules.includes('<-loopback>'))
+      const bypassesLoopback = proxyBypassRules.some(rule => rule === '<-loopback>' || rule === 'localhost' || rule === '127.0.0.1' || rule === '::1');
+      if (!process.env.PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK && !bypassesLoopback)
         proxyBypassRules.push('<-loopback>');
       if (proxyBypassRules.length > 0)
         chromeArguments.push(`--proxy-bypass-list=${proxyBypassRules.join(';')}`);
PATCH

echo "Patch applied successfully."

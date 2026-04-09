#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if grep -q "VERSION = '0.24.0'" apps/desktop/scripts/download-agent-browser.mjs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/apps/desktop/scripts/download-agent-browser.mjs b/apps/desktop/scripts/download-agent-browser.mjs
index 9ca7780c135..13b99b009fe 100644
--- a/apps/desktop/scripts/download-agent-browser.mjs
+++ b/apps/desktop/scripts/download-agent-browser.mjs
@@ -5,7 +5,7 @@ import path from 'node:path';
 import { pipeline } from 'node:stream/promises';
 import { fileURLToPath } from 'node:url';

-const VERSION = '0.20.1';
+const VERSION = '0.24.0';

 const __dirname = path.dirname(fileURLToPath(import.meta.url));
 const binDir = path.join(__dirname, '..', 'resources', 'bin');
PATCH

echo "Patch applied successfully."

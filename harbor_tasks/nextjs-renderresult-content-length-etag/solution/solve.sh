#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
# Check for a distinctive line from the fix: JSON.stringify without Buffer.from
if ! grep -q 'Buffer.from(JSON.stringify' packages/next/src/server/route-modules/pages/pages-handler.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

echo "Applying fixes..."

# Fix 1: Update AGENTS.md - replace incorrect bare --args with correct -- --args
sed -i 's/# Format: pnpm new-test --args <appDir> <name> <type>/# Format: pnpm new-test -- --args <appDir> <name> <type>/' AGENTS.md
sed -i 's/# Use --args for non-interactive mode$/# Use --args for non-interactive mode (forward args to the script using `--`)/' AGENTS.md
sed -i 's/pnpm new-test --args true my-feature e2e$/pnpm new-test -- --args true my-feature e2e/' AGENTS.md

# Fix the "Quick smoke testing" line
sed -i 's/generate a minimal test fixture with `pnpm new-test --args true/generate a minimal test fixture with `pnpm new-test -- --args true/' AGENTS.md

# Fix 2: Remove Buffer.from() wrapping in data request handler
sed -i ':a;N;$!ba;s/? new RenderResult(\n                  Buffer.from(JSON.stringify(result.value.pageData)),\n                  {\n                    contentType: JSON_CONTENT_TYPE_HEADER,\n                    metadata: result.value.html.metadata,\n                  }\n                )/? new RenderResult(JSON.stringify(result.value.pageData), {\n                  contentType: JSON_CONTENT_TYPE_HEADER,\n                  metadata: result.value.html.metadata,\n                })/g' packages/next/src/server/route-modules/pages/pages-handler.ts

# Fix 3: Remove Buffer.from() wrapping in cached HTML handler
sed -i ':a;N;$!ba;s/html: new RenderResult(\n                  Buffer.from(previousCacheEntry.value.html),\n                  {\n                    contentType: HTML_CONTENT_TYPE_HEADER,\n                    metadata: {\n                      statusCode: previousCacheEntry.value.status,\n                      headers: previousCacheEntry.value.headers,\n                    },\n                  }\n                ),/html: new RenderResult(previousCacheEntry.value.html, {\n                  contentType: HTML_CONTENT_TYPE_HEADER,\n                  metadata: {\n                    statusCode: previousCacheEntry.value.status,\n                    headers: previousCacheEntry.value.headers,\n                  },\n                }),/g' packages/next/src/server/route-modules/pages/pages-handler.ts

echo "Patch applied successfully."

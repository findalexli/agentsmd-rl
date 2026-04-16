#!/bin/bash
set -e

cd /workspace/router

# Idempotency check - skip if already applied
if grep -q "xmlns:xhtml" packages/start-plugin-core/src/build-sitemap.ts 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the fix using sed - add xmlns:xhtml after the xmlns line in the createXml function
sed -i "/xmlns: 'https:\/\/www.sitemaps.org\/schemas\/sitemap\/0.9',/a\\      'xmlns:xhtml': 'http://www.w3.org/1999/xhtml'," packages/start-plugin-core/src/build-sitemap.ts

echo "Patch applied successfully."

# Rebuild the affected package
pnpm nx run @tanstack/start-plugin-core:build --outputStyle=stream

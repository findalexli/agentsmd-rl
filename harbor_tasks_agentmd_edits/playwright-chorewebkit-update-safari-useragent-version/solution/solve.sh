#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q "const BROWSER_VERSION = '26.4'" packages/playwright-core/src/server/webkit/wkBrowser.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# 1. Update the BROWSER_VERSION constant (source of truth)
sed -i "s/const BROWSER_VERSION = '26.0'/const BROWSER_VERSION = '26.4'/" \
    packages/playwright-core/src/server/webkit/wkBrowser.ts

# 2. Update browsers.json
sed -i 's/"browserVersion": "26.0"/"browserVersion": "26.4"/' \
    packages/playwright-core/browsers.json

# 3. Update all device descriptor user-agent strings
sed -i 's/Version\/26\.0/Version\/26.4/g' \
    packages/playwright-core/src/server/deviceDescriptorsSource.json

# 4. Update README.md badge and table
sed -i 's/webkit-26\.0/webkit-26.4/g' README.md
sed -i 's/>26\.0</>26.4</g' README.md

# 5. Update release notes
for f in docs/src/release-notes-csharp.md docs/src/release-notes-java.md docs/src/release-notes-js.md docs/src/release-notes-python.md; do
    sed -i 's/WebKit 26\.0/WebKit 26.4/' "$f"
done

# 6. Create the new skill document
cat > .claude/skills/playwright-dev/webkit-safari-version.md << 'SKILLDOC'
# Updating WebKit Safari Version

The Safari version string used in the WebKit user-agent is declared in one place:

**[packages/playwright-core/src/server/webkit/wkBrowser.ts](../../../packages/playwright-core/src/server/webkit/wkBrowser.ts)** — `BROWSER_VERSION` constant (line ~35).

```ts
const BROWSER_VERSION = '26.4';
const DEFAULT_USER_AGENT = `Mozilla/5.0 ... Version/${BROWSER_VERSION} Safari/605.1.15`;
```

## Steps to update

1. **Find the latest stable Safari version** — search `site:developer.apple.com "Safari X.Y Release Notes"` or check the [Safari Release Notes](https://developer.apple.com/documentation/safari-release-notes) index. The highest numbered entry that is not a Technology Preview is the current stable release.

2. **Update `BROWSER_VERSION`** in `wkBrowser.ts`.

3. **Run lint** to update any generated files that embed the version:

   ```bash
   npm run flint
   ```
SKILLDOC

# 7. Update SKILL.md index to reference the new doc
sed -i '/Vendoring Dependencies/a - [Updating WebKit Safari Version](webkit-safari-version.md) — update the Safari version string in the WebKit user-agent' \
    .claude/skills/playwright-dev/SKILL.md

echo "Patch applied successfully."

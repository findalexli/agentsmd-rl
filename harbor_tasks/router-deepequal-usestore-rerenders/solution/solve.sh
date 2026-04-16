#!/bin/bash
set -e

cd /workspace/router

# Check if already patched (idempotency)
if grep -q "import { deepEqual } from '@tanstack/router-core'" packages/react-router/src/Scripts.tsx; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Fix Scripts.tsx
# Add deepEqual import after useStore import
sed -i "s|import { useStore } from '@tanstack/react-store'|import { useStore } from '@tanstack/react-store'\nimport { deepEqual } from '@tanstack/router-core'|" packages/react-router/src/Scripts.tsx

# Fix useStore calls in Scripts.tsx - add deepEqual as third argument
# For assetScripts useStore call
sed -i 's|getAssetScripts,\n  )|getAssetScripts,\n    deepEqual,\n  )|g' packages/react-router/src/Scripts.tsx || true

# For scripts useStore call - convert single line to multi-line with deepEqual
sed -i 's|const scripts = useStore(router.stores.activeMatchesSnapshot, getScripts)|const scripts = useStore(\n    router.stores.activeMatchesSnapshot,\n    getScripts,\n    deepEqual,\n  )|g' packages/react-router/src/Scripts.tsx

# Fix headContentUtils.tsx - update the import line
sed -i "s|import { escapeHtml } from '@tanstack/router-core'|import { deepEqual, escapeHtml } from '@tanstack/router-core'|" packages/react-router/src/headContentUtils.tsx

# Fix useTags hook - add deepEqual to all useStore calls
# We'll use a Python script for more complex multi-line replacements
cat > /tmp/fix_headutils.py << 'PYEOF'
import re

filepath = "packages/react-router/src/headContentUtils.tsx"
with open(filepath, 'r') as f:
    content = f.read()

# Fix routeMeta useStore call
old_routeMeta = """  const routeMeta = useStore(router.stores.activeMatchesSnapshot, (matches) => {
    return matches.map((match) => match.meta!).filter(Boolean)
  })"""

new_routeMeta = """  const routeMeta = useStore(
    router.stores.activeMatchesSnapshot,
    (matches) => {
      return matches.map((match) => match.meta!).filter(Boolean)
    },
    deepEqual,
  )"""

content = content.replace(old_routeMeta, new_routeMeta)

# Fix links useStore call
old_links = """  const links = useStore(router.stores.activeMatchesSnapshot, (matches) => {
    const constructed = matches
      .map((match) => match.links!)
      .filter(Boolean)
      .flat(1)
      .map((link) => ({
        tag: 'link',
        attrs: {
          ...link,
          nonce,
        },
      })) satisfies Array<RouterManagedTag>

    const manifest = router.ssr?.manifest

    // These are the assets extracted from the ViteManifest
    // using the `startManifestPlugin`
    const assets = matches
      .map((match) => manifest?.routes[match.routeId]?.assets ?? [])
      .filter(Boolean)
      .flat(1)
      .filter((asset) => asset.tag === 'link')
      .map(
        (asset) =>
          ({
            tag: 'link',
            attrs: {
              ...asset.attrs,
              suppressHydrationWarning: true,
              nonce,
            },
          }) satisfies RouterManagedTag,
      )

    return [...constructed, ...assets]
  })"""

new_links = """  const links = useStore(
    router.stores.activeMatchesSnapshot,
    (matches) => {
      const constructed = matches
        .map((match) => match.links!)
        .filter(Boolean)
        .flat(1)
        .map((link) => ({
          tag: 'link',
          attrs: {
            ...link,
            nonce,
          },
        })) satisfies Array<RouterManagedTag>

      const manifest = router.ssr?.manifest

      // These are the assets extracted from the ViteManifest
      // using the `startManifestPlugin`
      const assets = matches
        .map((match) => manifest?.routes[match.routeId]?.assets ?? [])
        .filter(Boolean)
        .flat(1)
        .filter((asset) => asset.tag === 'link')
        .map(
          (asset) =>
            ({
              tag: 'link',
              attrs: {
                ...asset.attrs,
                suppressHydrationWarning: true,
                nonce,
              },
            }) satisfies RouterManagedTag,
        )

      return [...constructed, ...assets]
    },
    deepEqual,
  )"""

content = content.replace(old_links, new_links)

# Fix preloadLinks useStore call - add deepEqual as third argument before closing paren
old_preload = """  const preloadLinks = useStore(
    router.stores.activeMatchesSnapshot,
    (matches) => {
      const preloadLinks = []

      // ... rest of the function

      return preloadLinks
    },
  )"""

# Find and fix preloadLinks - look for the pattern and add deepEqual
preload_pattern = r'(const preloadLinks = useStore\(\s*router\.stores\.activeMatchesSnapshot,\s*\(matches\) => \{[\s\S]*?return preloadLinks\s*\},)'
content = re.sub(preload_pattern, r'\1\n    deepEqual,', content)

# Fix styles useStore call
old_styles = """  const styles = useStore(router.stores.activeMatchesSnapshot, (matches) =>
    (
      matches
        .map((match) => match.styles!)
        .flat(1)
        .filter(Boolean) as Array<RouterManagedTag>
    ).map(({ children, ...attrs }) => ({
      tag: 'style',
      attrs: {
        ...attrs,
        nonce,
      },
      children,
    })),
  )"""

new_styles = """  const styles = useStore(
    router.stores.activeMatchesSnapshot,
    (matches) =>
      (
        matches
          .map((match) => match.styles!)
          .flat(1)
          .filter(Boolean) as Array<RouterManagedTag>
      ).map(({ children, ...attrs }) => ({
        tag: 'style',
        attrs: {
          ...attrs,
          nonce,
        },
        children,
      })),
    deepEqual,
  )"""

content = content.replace(old_styles, new_styles)

# Fix headScripts useStore call
old_scripts = """  const headScripts: Array<RouterManagedTag> = useStore(
    router.stores.activeMatchesSnapshot,
    (matches) =>
      (
        matches
          .map((match) => match.headScripts!)
          .flat(1)
          .filter(Boolean) as Array<RouterManagedTag>
      ).map(({ children, ...script }) => ({
        tag: 'script',
        attrs: {
          ...script,
          nonce,
        },
        children,
      })),
  )"""

new_scripts = """  const headScripts: Array<RouterManagedTag> = useStore(
    router.stores.activeMatchesSnapshot,
    (matches) =>
      (
        matches
          .map((match) => match.headScripts!)
          .flat(1)
          .filter(Boolean) as Array<RouterManagedTag>
      ).map(({ children, ...script }) => ({
        tag: 'script',
        attrs: {
          ...script,
          nonce,
        },
        children,
      })),
    deepEqual,
  )"""

content = content.replace(old_scripts, new_scripts)

with open(filepath, 'w') as f:
    f.write(content)

print("headContentUtils.tsx fixed successfully")
PYEOF

python3 /tmp/fix_headutils.py

# Now manually fix Scripts.tsx with a Python script too
cat > /tmp/fix_scripts.py << 'PYEOF'
import re

filepath = "packages/react-router/src/Scripts.tsx"
with open(filepath, 'r') as f:
    content = f.read()

# Fix assetScripts useStore call
old_asset = """  const assetScripts = useStore(
    router.stores.activeMatchesSnapshot,
    getAssetScripts,
  )"""

new_asset = """  const assetScripts = useStore(
    router.stores.activeMatchesSnapshot,
    getAssetScripts,
    deepEqual,
  )"""

content = content.replace(old_asset, new_asset)

# Fix scripts useStore call
old_scripts = "const scripts = useStore(router.stores.activeMatchesSnapshot, getScripts)"
new_scripts = """const scripts = useStore(
    router.stores.activeMatchesSnapshot,
    getScripts,
    deepEqual,
  )"""

content = content.replace(old_scripts, new_scripts)

with open(filepath, 'w') as f:
    f.write(content)

print("Scripts.tsx fixed successfully")
PYEOF

python3 /tmp/fix_scripts.py

echo "Patch applied successfully"

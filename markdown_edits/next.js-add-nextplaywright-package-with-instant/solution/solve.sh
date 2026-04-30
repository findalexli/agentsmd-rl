#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if [ -f packages/next-playwright/src/index.ts ]; then
    echo "Patch already applied."
    exit 0
fi

# Create the @next/playwright package directory structure
mkdir -p packages/next-playwright/src

# --- packages/next-playwright/package.json ---
cat > packages/next-playwright/package.json <<'PKG_EOF'
{
  "name": "@next/playwright",
  "version": "16.2.0-canary.59",
  "private": true,
  "repository": {
    "url": "vercel/next.js",
    "directory": "packages/next-playwright"
  },
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": [
    "dist"
  ],
  "license": "MIT",
  "scripts": {
    "build": "node ../../scripts/rm.mjs dist && tsc -d -p tsconfig.json",
    "prepublishOnly": "cd ../../ && turbo run build",
    "dev": "tsc -d -w -p tsconfig.json",
    "typescript": "tsec --noEmit -p tsconfig.json"
  },
  "devDependencies": {
    "typescript": "5.9.2"
  }
}
PKG_EOF

# --- packages/next-playwright/tsconfig.json ---
cat > packages/next-playwright/tsconfig.json <<'TSC_EOF'
{
  "compilerOptions": {
    "strict": true,
    "esModuleInterop": true,
    "target": "es2019",
    "outDir": "dist",
    "module": "commonjs",
    "rootDir": "src",
    "declaration": true
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules"]
}
TSC_EOF

# --- packages/next-playwright/src/index.ts ---
cat > packages/next-playwright/src/index.ts <<'SRC_EOF'
/**
 * Minimal interface for Playwright's Page. We use a structural type rather than
 * importing from a specific Playwright package so this works with any version
 * of playwright, playwright-core, or @playwright/test.
 */
interface PlaywrightPage {
  evaluate<R, Arg>(pageFunction: (arg: Arg) => R, arg: Arg): Promise<R>
}

const INSTANT_COOKIE = 'next-instant-navigation-testing'

/**
 * Runs a function with instant navigation enabled. Within this scope,
 * navigations render the prefetched UI immediately and wait for the
 * callback to complete before streaming in dynamic data.
 *
 * Uses the cookie-based protocol: setting the cookie acquires the
 * navigation lock (via CookieStore change event), and clearing it
 * releases the lock.
 */
export async function instant<T>(
  page: PlaywrightPage,
  fn: () => Promise<T>
): Promise<T> {
  // Acquire the lock by setting the cookie from within the page context.
  // This triggers the CookieStore change event in navigation-testing-lock.ts,
  // which acquires the in-memory navigation lock.
  await page.evaluate((name) => {
    document.cookie = name + '=1; path=/'
  }, INSTANT_COOKIE)
  try {
    return await fn()
  } finally {
    // Release the lock by clearing the cookie. For SPA navigations, this
    // triggers the CookieStore change event which resolves the in-memory
    // lock. For MPA navigations (reload, plain anchor), the listener in
    // app-bootstrap.ts triggers a page reload to fetch dynamic data.
    await page.evaluate((name) => {
      document.cookie = name + '=; path=/; max-age=0'
    }, INSTANT_COOKIE)
  }
}
SRC_EOF

# --- packages/next-playwright/README.md ---
cat > packages/next-playwright/README.md <<'README_EOF'
# @next/playwright

> - **Status:** Experimental. This API is not yet stable.
> - **Requires:** [Cache Components](https://nextjs.org/docs) to be enabled.

Playwright helpers for testing Next.js applications.

## Instant Navigation Testing

An **instant navigation** commits immediately without waiting for data fetching.
The cached shell — including any Suspense loading boundaries — renders right
away, and dynamic data streams in afterward. The shell is the instant part, not
the full page.

`instant()` lets you test whether a route achieves this. While the callback is
active, navigations render only cached and prefetched content. Dynamic data is
deferred until the callback returns. This lets you make deterministic assertions
against the shell without race conditions.

The tool assumes a warm cache: all prefetches have completed and all cacheable
data is available. This way you're testing whether the route is *structured
correctly* for instant navigation, independent of network timing. If content you
expected to be cached is missing inside the callback, it points to a problem — a
missing `use cache` directive, a misplaced Suspense boundary, or a similar gap.

### Examples

**Loading shell appears instantly** (dynamic content behind a Suspense boundary):

```ts
import { instant } from '@next/playwright'

test('shows loading shell during navigation', async ({ page }) => {
  await page.goto('/')

  await instant(page, async () => {
    await page.click('a[href="/dashboard"]')

    // The loading shell is visible — dynamic data is deferred
    await expect(page.locator('[data-testid="loading"]')).toBeVisible()
  })

  // After instant() returns, dynamic data streams in normally
  await expect(page.locator('[data-testid="content"]')).toBeVisible()
})
```

**Fully instant navigation** (all content is cached):

```ts
test('navigates to profile instantly', async ({ page }) => {
  await page.goto('/')

  await instant(page, async () => {
    await page.click('a[href="/profile"]')

    // All content renders immediately
    await expect(page.locator('[data-testid="profile-name"]')).toBeVisible()
    await expect(page.locator('[data-testid="profile-bio"]')).toBeVisible()
  })
})
```

### Enabling in production builds

In development (`next dev`), the testing API is available by default. In
production builds, it is disabled unless you explicitly opt in:

```js
// next.config.js
module.exports = {
  experimental: {
    exposeTestingApiInProductionBuild: true,
  },
}
```

This is not meant to be deployed to live production sites. Only enable it in
controlled testing environments like preview deployments or CI.

## How it works

`instant()` sets a cookie that tells Next.js to serve only cached data during
navigations. While the cookie is active:

- **Client-side navigations**: The router renders only what is available in the
  prefetch cache. Dynamic data is deferred until the cookie is cleared.
- **Server renders (initial load, reload, MPA navigation)**: The server responds
  with only the static shell, without any per-request dynamic data.

When the callback completes, the cookie is cleared and normal behavior resumes.

## Design

The layering between this package and Next.js is intentionally very thin. This
serves as a reference implementation that other testing frameworks and dev tools
can replicate with minimal effort. The entire mechanism is a single cookie:

```ts
// Set the cookie to enter instant mode
document.cookie = 'next-instant-navigation-testing=1; path=/'

// ... run assertions ...

// Clear the cookie to resume normal behavior
document.cookie = 'next-instant-navigation-testing=; path=/; max-age=0'
```
README_EOF

# --- Modify root tsconfig.json to add @next/playwright path alias ---
python3 -c "
import json, re

with open('tsconfig.json') as f:
    raw = f.read()

# Strip comments for parsing
stripped = re.sub(r'//.*', '', raw)
stripped = re.sub(r',\s*([}\]])', r'\1', stripped)
data = json.loads(stripped)

# Add path alias
paths = data.setdefault('compilerOptions', {}).setdefault('paths', {})
paths['@next/playwright'] = ['./packages/next-playwright/src/index.ts']

# We need to write back preserving rough structure — use the raw file approach
# Insert the new path before the closing of paths object
import re as re2
# Find the last path entry and add after it
raw_new = raw.replace(
    '\"router-act\": [\"./test/lib/router-act\"]',
    '\"router-act\": [\"./test/lib/router-act\"],\n      \"@next/playwright\": [\"./packages/next-playwright/src/index.ts\"]'
)
with open('tsconfig.json', 'w') as f:
    f.write(raw_new)
"

echo "Patch applied successfully."

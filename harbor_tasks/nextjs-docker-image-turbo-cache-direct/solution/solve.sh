#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'computeCacheKey' scripts/docker-image-cache.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.github/workflows/build_and_deploy.yml b/.github/workflows/build_and_deploy.yml
index 61d15d00f92667..9065e27002d7f6 100644
--- a/.github/workflows/build_and_deploy.yml
+++ b/.github/workflows/build_and_deploy.yml
@@ -246,14 +246,10 @@ jobs:
       - name: Clear native build
         run: rm -rf packages/next-swc/native

-      # Build or restore the Docker image via turbo remote cache.
-      # Step 1: turbo either runs the build (cache miss) or restores image.tar (cache hit).
-      # Step 2: --load ensures the tar is loaded into docker (turbo skips the script on hit).
+      # Build or restore the Docker image via turbo-cache.js.
       - name: Build/restore Docker image
         if: ${{ matrix.docker }}
-        run: |
-          pnpm dlx turbo@${TURBO_VERSION} run build-docker-image --remote-cache-timeout 90 --log-order stream
-          node scripts/docker-image-cache.js --load
+        run: node scripts/docker-image-cache.js

       # Try to restore previously-built native binary from turbo cache
       - name: pull build cache
diff --git a/packages/next-swc/package.json b/packages/next-swc/package.json
index 7bd1e8ca9fb7ba..6c9ee7f3398af9 100644
--- a/packages/next-swc/package.json
+++ b/packages/next-swc/package.json
@@ -15,7 +15,6 @@
     "build-native-no-plugin-release": "napi build --platform -p next-napi-bindings --cargo-cwd ../../ --cargo-name next_napi_bindings --release --features image-webp,tracing/release_max_level_trace --js false native",
     "build-native-wasi": "npx --package=@napi-rs/cli@3.0.0-alpha.45 napi build --platform --target wasm32-wasip1-threads -p next-napi-bindings --cwd ../../ --output-dir packages/next-swc/native --no-default-features",
     "build-wasm": "wasm-pack build ../../crates/wasm --scope=next",
-    "build-docker-image": "node ../../scripts/docker-image-cache.js",
     "cache-build-native": "[ -d native ] && echo $(ls native)",
     "rust-check-clippy": "cargo clippy --workspace --all-targets -- -D warnings -A deprecated",
     "rust-check-doc": "RUSTDOCFLAGS='-Zunstable-options --output-format=json' cargo doc --no-deps --workspace",
diff --git a/packages/next-swc/turbo.jsonc b/packages/next-swc/turbo.jsonc
index fce47a75521d29..36fced8ad23681 100644
--- a/packages/next-swc/turbo.jsonc
+++ b/packages/next-swc/turbo.jsonc
@@ -121,14 +121,6 @@
       "env": ["CI"],
       "outputs": ["native/*"],
     },
-    "build-docker-image": {
-      "inputs": [
-        "../../scripts/native-builder.Dockerfile",
-        "../../scripts/docker-native-build.sh",
-        "../../rust-toolchain.toml",
-      ],
-      "outputs": ["../../target/docker-image.tar"],
-    },
     "cache-build-native": {
       "inputs": [
         "../../.cargo/**",
diff --git a/scripts/docker-image-cache.js b/scripts/docker-image-cache.js
index d0c7830695f887..4b5e8371909c07 100644
--- a/scripts/docker-image-cache.js
+++ b/scripts/docker-image-cache.js
@@ -1,26 +1,17 @@
 #!/usr/bin/env node
-// @ts-check
 //
-// Build or restore the next-swc-builder Docker image.
+// Build or restore the next-swc-builder Docker image using turbo remote cache.
 //
-// This script is both a turbo task AND a post-turbo loader:
-//
-// 1. `pnpm -F @next/swc build-docker-image` (turbo task):
-//    - On cache miss: turbo runs this script, which builds the image and saves
-//      target/docker-image.tar for turbo to cache as output.
-//    - On cache hit: turbo restores target/docker-image.tar and SKIPS this script.
-//
-// 2. `node scripts/docker-image-cache.js --load` (post-turbo step):
-//    - If target/docker-image.tar exists (turbo cache hit), loads it into docker.
-//    - If the image is already loaded, does nothing.
-//    - Cleans up the tar after loading.
+// Computes a cache key from the Dockerfile + rust-toolchain.toml contents,
+// then checks the turbo cache API via scripts/turbo-cache.mjs.
+// Images are compressed with zstd before upload (~2.8GB → ~500MB).
 //
 // Usage:
-//   node scripts/docker-image-cache.js           # build image + save tar (turbo task)
-//   node scripts/docker-image-cache.js --load    # load tar into docker if present
-//   node scripts/docker-image-cache.js --force   # always rebuild
+//   node scripts/docker-image-cache.js           # restore from cache or build + upload
+//   node scripts/docker-image-cache.js --force   # always rebuild and re-upload

-const { execSync } = require('child_process')
+const { execSync, spawn } = require('child_process')
+const { createHash } = require('crypto')
 const path = require('path')
 const fs = require('fs')
 const os = require('os')
@@ -30,23 +21,30 @@ const { values: flags } = parseArgs({
   args: process.argv.slice(2),
   options: {
     force: { type: 'boolean', default: false },
-    load: { type: 'boolean', default: false },
   },
 })

 const REPO_ROOT = path.resolve(__dirname, '..')
 const IMAGE_NAME = 'next-swc-builder:latest'
-const IMAGE_TAR = path.join(REPO_ROOT, 'target/docker-image.tar')
-const force = flags.force
-const load = flags.load

-function imageExists() {
-  try {
-    execSync(`docker image inspect ${IMAGE_NAME}`, { stdio: 'ignore' })
-    return true
-  } catch {
-    return false
+// Files that determine the docker image content — if any change, rebuild.
+const CACHE_INPUTS = [
+  path.join(REPO_ROOT, 'scripts/native-builder.Dockerfile'),
+  path.join(REPO_ROOT, 'scripts/docker-image-cache.js'),
+  path.join(REPO_ROOT, 'scripts/docker-native-build.js'),
+  path.join(REPO_ROOT, 'scripts/docker-native-build.sh'),
+  path.join(REPO_ROOT, 'rust-toolchain.toml'),
+]
+
+function computeCacheKey() {
+  // Turbo cache keys must be hex-only (^[a-fA-F0-9]+$).
+  const hash = createHash('sha256')
+  hash.update('docker-image-v3\0')
+  for (const file of CACHE_INPUTS) {
+    hash.update(file + '\0')
+    hash.update(fs.readFileSync(file))
   }
+  return hash.digest('hex')
 }

 function buildImage() {
@@ -66,30 +64,97 @@ function buildImage() {
   }
 }

-if (load) {
-  // Post-turbo step: load the cached tar if present, or build if missing
-  if (imageExists() && !force) {
-    console.log('Docker image already loaded')
-  } else if (fs.existsSync(IMAGE_TAR)) {
-    console.log('Loading Docker image from turbo cache...')
-    execSync(`docker load -i ${IMAGE_TAR}`, { stdio: 'inherit' })
-    fs.unlinkSync(IMAGE_TAR)
-    console.log('Docker image restored from cache')
-  } else {
-    console.log('No cached image — building from scratch')
+function tmpFile(name) {
+  return path.join(process.env.RUNNER_TEMP || os.tmpdir(), name)
+}
+
+function sh(cmd) {
+  execSync(cmd, { stdio: 'inherit', shell: true })
+}
+
+/** Pipe a Node.js Readable stream into a shell command's stdin. */
+function pipeToShell(stream, cmd) {
+  return new Promise((resolve, reject) => {
+    const child = spawn(cmd, {
+      stdio: ['pipe', 'inherit', 'inherit'],
+      shell: true,
+    })
+    stream.pipe(child.stdin)
+    stream.on('error', (err) => {
+      child.kill()
+      reject(err)
+    })
+    child.on('error', reject)
+    child.on('close', (code) => {
+      if (code !== 0) reject(new Error(`Command failed with exit code ${code}`))
+      else resolve()
+    })
+  })
+}
+
+async function main() {
+  const cache = await import('./turbo-cache.mjs')
+  const key = computeCacheKey()
+  console.log(`Docker image cache key: ${key}`)
+
+  if (!process.env.TURBO_TOKEN) {
+    console.log('No TURBO_TOKEN — building without cache')
     buildImage()
+    return
   }
-} else {
-  // Turbo task: build and save tar for caching
-  if (force && fs.existsSync(IMAGE_TAR)) fs.unlinkSync(IMAGE_TAR)
-  if (!imageExists() || force) {
-    buildImage()
+
+  // Try to restore from cache (unless --force)
+  if (!flags.force) {
+    const hit = await cache.exists(key)
+    console.log(hit ? 'Cache HIT' : 'Cache MISS')
+
+    if (hit) {
+      try {
+        console.log('Streaming cached image through zstd into docker load...')
+        const stream = await cache.getStream(key)
+        await pipeToShell(stream, `zstd -d | docker load`)
+        console.log('Docker image restored from turbo cache')
+        return
+      } catch (e) {
+        console.log(`WARNING: Failed to restore image: ${e.message}`)
+        console.log('Discarding cached image and rebuilding from scratch')
+        // Remove the partially-loaded image if it exists
+        try {
+          execSync(`docker rmi -f ${IMAGE_NAME}`, { stdio: 'ignore' })
+        } catch {}
+      }
+    }
   }
-  if (!fs.existsSync(IMAGE_TAR)) {
-    console.log('Saving Docker image for turbo cache...')
-    fs.mkdirSync(path.dirname(IMAGE_TAR), { recursive: true })
-    execSync(`docker save ${IMAGE_NAME} -o ${IMAGE_TAR}`, { stdio: 'inherit' })
-    const size = fs.statSync(IMAGE_TAR).size
-    console.log(`Saved: ${(size / 1024 / 1024).toFixed(0)} MB`)
+
+  // Cache miss or --force: always rebuild since inputs changed
+  buildImage()
+
+  // Compress and upload
+  console.log('Compressing docker image with zstd...')
+  const zstdFile = tmpFile('docker-image-cache.tar.zst')
+  try {
+    sh(`docker save ${IMAGE_NAME} | zstd -3 -T0 -o ${zstdFile}`)
+
+    const size = fs.statSync(zstdFile).size
+    console.log(
+      `Compressed: ${(size / 1024 / 1024).toFixed(0)} MB — uploading...`
+    )
+
+    try {
+      // Stream upload from file (avoids 2GB Buffer limit)
+      await cache.put(key, zstdFile)
+      console.log('Docker image uploaded to turbo cache')
+    } catch (e) {
+      console.log(`WARNING: Failed to upload: ${e.message}`)
+    }
+  } finally {
+    try {
+      fs.unlinkSync(zstdFile)
+    } catch {}
   }
 }
+
+main().catch((e) => {
+  console.error(e)
+  process.exit(1)
+})
diff --git a/scripts/docker-native-build.js b/scripts/docker-native-build.js
index 0289cbd7fb22cf..777aa74c0c8427 100755
--- a/scripts/docker-native-build.js
+++ b/scripts/docker-native-build.js
@@ -8,7 +8,7 @@
 //   --test         Smoke-test built binaries (native arch only)
 //   filter         Substring match on target name (e.g. "musl", "x86_64")

-const { execSync, execFileSync } = require('child_process')
+const { execFileSync } = require('child_process')
 const path = require('path')
 const fs = require('fs')
 const os = require('os')
@@ -85,30 +85,13 @@ if (targets.length === 0) {
   process.exit(1)
 }

-// --- Build Docker image via turbo task ---
-// Step 1: turbo either builds (cache miss) or restores image.tar (cache hit).
-// Step 2: --load ensures the image is in docker (turbo skips the script on hit).
+// --- Build/restore Docker image ---
 function ensureDockerImage() {
-  try {
-    execSync(`docker image inspect ${DOCKER_IMAGE}`, { stdio: 'ignore' })
-    if (!rebuild) return // already loaded
-  } catch {
-    // not loaded — continue to build/restore
-  }
-
-  const forceFlag = rebuild ? ' -- --force' : ''
-  execSync(`pnpm -F @next/swc build-docker-image${forceFlag}`, {
-    stdio: 'inherit',
-    cwd: REPO_ROOT,
-  })
-  // Load the image if turbo restored it from cache (turbo skips the script on hit)
-  const loadFlag = rebuild ? '--force' : '--load'
+  const args = rebuild ? ['--force'] : []
   execFileSync(
     'node',
-    [path.join(__dirname, 'docker-image-cache.js'), loadFlag],
-    {
-      stdio: 'inherit',
-    }
+    [path.join(__dirname, 'docker-image-cache.js'), ...args],
+    { stdio: 'inherit' }
   )
 }

diff --git a/scripts/turbo-cache.mjs b/scripts/turbo-cache.mjs
new file mode 100644
index 00000000000000..6a1fea912e712e
--- /dev/null
+++ b/scripts/turbo-cache.mjs
@@ -0,0 +1,165 @@
+// Turbo remote cache client.
+//
+// Provides exists/get/put operations against the Vercel turbo remote cache API.
+// Handles both vercel.com (/api/v8/artifacts/) and custom self-hosted servers
+// (/v8/artifacts/).
+//
+// put() accepts either a Buffer/Uint8Array or a string path to stream from disk
+// (for large files that exceed Node's 2GB Buffer limit).
+//
+// Usage:
+//   import * as cache from './turbo-cache.mjs'
+//   await cache.exists(hexKey)          // -> boolean
+//   await cache.get(hexKey)             // -> Buffer | null
+//   await cache.put(hexKey, buffer)     // upload from memory
+//   await cache.put(hexKey, '/path')    // stream upload from file
+
+import fs from 'fs'
+import { createHash } from 'crypto'
+import { Readable } from 'stream'
+
+const TURBO_API = process.env.TURBO_API || 'https://vercel.com'
+const TURBO_TOKEN = process.env.TURBO_TOKEN
+const TURBO_TEAM = process.env.TURBO_TEAM
+
+const IS_VERCEL = new URL(TURBO_API).hostname === 'vercel.com'
+
+// Vercel's cache API lives at /api/v8/artifacts/ and uses ?teamId=.
+// Self-hosted turbo cache servers use /v8/artifacts/ and ?slug=.
+export function artifactUrl(key) {
+  if (IS_VERCEL) {
+    const qs = TURBO_TEAM ? `?teamId=${TURBO_TEAM}` : ''
+    return `https://vercel.com/api/v8/artifacts/${key}${qs}`
+  }
+  const qs = TURBO_TEAM ? `?slug=${TURBO_TEAM}` : ''
+  return `${TURBO_API}/v8/artifacts/${key}${qs}`
+}
+
+function baseHeaders() {
+  return {
+    Authorization: `Bearer ${TURBO_TOKEN}`,
+    'User-Agent': 'turbo 2 next.js-ci',
+    'x-artifact-client-ci': 'GITHUB_ACTIONS',
+  }
+}
+
+/** Check if an artifact exists. */
+export async function exists(key) {
+  const res = await fetch(artifactUrl(key), {
+    method: 'HEAD',
+    headers: baseHeaders(),
+  })
+  return res.status === 200
+}
+
+/** Download an artifact. Returns Buffer on hit, null on miss. */
+export async function get(key) {
+  const res = await fetch(artifactUrl(key), {
+    method: 'GET',
+    headers: baseHeaders(),
+  })
+  if (!res.ok) return null
+  return Buffer.from(await res.arrayBuffer())
+}
+
+/**
+ * Download an artifact as a Node.js Readable stream. Throws on failure.
+ */
+export async function getStream(key) {
+  const res = await fetch(artifactUrl(key), {
+    method: 'GET',
+    headers: baseHeaders(),
+  })
+  if (!res.ok) {
+    throw new Error(`GET ${key} failed: ${res.status} ${res.statusText}`)
+  }
+  return Readable.fromWeb(res.body)
+}
+
+/**
+ * Upload an artifact.
+ * @param {string} key - hex-only cache key
+ * @param {Buffer|Uint8Array|string} data - Buffer/Uint8Array for in-memory,
+ *   or a string file path to stream from disk (for large files).
+ */
+export async function put(key, data) {
+  const isFile = typeof data === 'string'
+  const size = isFile ? fs.statSync(data).size : data.length
+
+  const headers = {
+    ...baseHeaders(),
+    'Content-Type': 'application/octet-stream',
+    'Content-Length': String(size),
+    'x-artifact-duration': '0',
+  }
+
+  let body
+  if (isFile) {
+    // Stream from file — avoids loading into memory
+    body = Readable.toWeb(fs.createReadStream(data))
+  } else {
+    body = data
+  }
+
+  const res = await fetch(artifactUrl(key), {
+    method: 'PUT',
+    headers,
+    body,
+    // Required for streaming request bodies in Node fetch
+    duplex: isFile ? 'half' : undefined,
+  })
+
+  if (!res.ok) {
+    const text = await res.text().catch(() => '')
+    throw new Error(
+      `PUT ${key} failed: ${res.status} ${res.statusText} ${text.slice(0, 200)}`
+    )
+  }
+}
+
+/**
+ * Verify read+write access. Returns true if both work.
+ */
+export async function healthCheck() {
+  const testKey = createHash('sha256')
+    .update(`turbo-cache-health-${Date.now()}`)
+    .digest('hex')
+
+  console.error(`Turbo cache health check:`)
+  console.error(`  API: ${IS_VERCEL ? 'vercel.com' : TURBO_API}`)
+  console.error(`  Team: ${TURBO_TEAM || '(none)'}`)
+  console.error(
+    `  Token: ${TURBO_TOKEN ? TURBO_TOKEN.slice(0, 8) + '...' : '(not set)'}`
+  )
+
+  if (!TURBO_TOKEN) {
+    console.error('  SKIP: no TURBO_TOKEN')
+    return false
+  }
+
+  try {
+    // READ
+    const e = await exists(testKey)
+    console.error(`  READ:   exists -> ${e}`)
+
+    // WRITE
+    const testData = Buffer.from('turbo-cache-write-test')
+    await put(testKey, testData)
+    console.error(`  WRITE:  put -> OK`)
+
+    // VERIFY
+    const readBack = await get(testKey)
+    if (readBack && readBack.equals(testData)) {
+      console.error(`  VERIFY: get -> OK (${readBack.length}B)`)
+    } else {
+      console.error(
+        `  VERIFY: get -> mismatch (${readBack ? readBack.length : 0}B)`
+      )
+    }
+
+    return true
+  } catch (e) {
+    console.error(`  FAIL: ${e.message}`)
+    return false
+  }
+}

PATCH

echo "Patch applied successfully."

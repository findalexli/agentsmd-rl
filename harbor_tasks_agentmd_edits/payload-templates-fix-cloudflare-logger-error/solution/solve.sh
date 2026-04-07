#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotent: skip if already applied
if grep -q 'cloudflareLogger' templates/with-cloudflare-d1/src/payload.config.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/payload/src/index.ts b/packages/payload/src/index.ts
index 1a377359bc2..51d718152c5 100644
--- a/packages/payload/src/index.ts
+++ b/packages/payload/src/index.ts
@@ -1812,6 +1812,7 @@ export { isValidID } from './utilities/isValidID.js'
 export { killTransaction } from './utilities/killTransaction.js'
 export { logError } from './utilities/logError.js'
 export { defaultLoggerOptions } from './utilities/logger.js'
+export type { PayloadLogger } from './utilities/logger.js'
 export { mapAsync } from './utilities/mapAsync.js'
 export { mergeHeaders } from './utilities/mergeHeaders.js'
 export { parseDocumentID } from './utilities/parseDocumentID.js'
diff --git a/templates/with-cloudflare-d1/README.md b/templates/with-cloudflare-d1/README.md
index 3bc4d878e6c..a58e16b4a0b 100644
--- a/templates/with-cloudflare-d1/README.md
+++ b/templates/with-cloudflare-d1/README.md
@@ -84,6 +84,24 @@ That's it! You can if you wish move these steps into your CI pipeline as well.

 By default logs are not enabled for your API, we've made this decision because it does run against your quota so we've left it opt-in. But you can easily enable logs in one click in the Cloudflare panel, [see docs](https://developers.cloudflare.com/workers/observability/logs/workers-logs/#enable-workers-logs).

+### Logger Configuration
+
+This template includes a custom console-based logger compatible with Cloudflare Workers. Payload's default logger uses `pino-pretty`, which relies on Node.js APIs not available in Workers and would cause `fs.write is not implemented` errors.
+
+The custom logger in `payload.config.ts`:
+
+- Routes logs through `console.*` methods which Workers handles correctly
+- Outputs JSON-formatted logs for Cloudflare observability
+- Only active in production (development uses the default `pino-pretty` for better DX)
+
+You can control the log level via the `PAYLOAD_LOG_LEVEL` environment variable (e.g., `debug`, `info`, `warn`, `error`).
+
+### Diagnostic Channel Errors
+
+If you see "Failed to publish diagnostic channel message" errors in your observability logs, these typically come from the `undici` HTTP client library. The template includes `skipSafeFetch: true` in the Media collection to use native fetch instead of undici for file uploads, which helps reduce these errors.
+
+Cloudflare Workers runs in an [isolated environment that cannot access private IP ranges](https://developers.cloudflare.com/workers-vpc/examples/route-across-private-services/) by default, providing built-in SSRF protection. This makes `skipSafeFetch` safe to use.
+
 ## Known issues

 ### GraphQL
diff --git a/templates/with-cloudflare-d1/eslint.config.mjs b/templates/with-cloudflare-d1/eslint.config.mjs
index 7acd77dd1b3..2dce39bdf0f 100644
--- a/templates/with-cloudflare-d1/eslint.config.mjs
+++ b/templates/with-cloudflare-d1/eslint.config.mjs
@@ -7,6 +7,7 @@ const __dirname = dirname(__filename)

 const compat = new FlatCompat({
   baseDirectory: __dirname,
+  resolvePluginsRelativeTo: __dirname,
 })

 const eslintConfig = [
diff --git a/templates/with-cloudflare-d1/package.json b/templates/with-cloudflare-d1/package.json
index 910358e6504..fb2e246f1e4 100644
--- a/templates/with-cloudflare-d1/package.json
+++ b/templates/with-cloudflare-d1/package.json
@@ -40,6 +40,7 @@
     "react-dom": "19.2.1"
   },
   "devDependencies": {
+    "@eslint/eslintrc": "^3.2.0",
     "@playwright/test": "1.58.2",
     "@testing-library/react": "16.3.0",
     "@types/node": "22.19.9",
diff --git a/templates/with-cloudflare-d1/src/payload.config.ts b/templates/with-cloudflare-d1/src/payload.config.ts
index 30333661f29..da3d5fef44a 100644
--- a/templates/with-cloudflare-d1/src/payload.config.ts
+++ b/templates/with-cloudflare-d1/src/payload.config.ts
@@ -18,6 +18,26 @@ const realpath = (value: string) => (fs.existsSync(value) ? fs.realpathSync(valu
 const isCLI = process.argv.some((value) => realpath(value).endsWith(path.join('payload', 'bin.js')))
 const isProduction = process.env.NODE_ENV === 'production'

+const createLog =
+  (level: string, fn: typeof console.log) => (objOrMsg: object | string, msg?: string) => {
+    if (typeof objOrMsg === 'string') {
+      fn(JSON.stringify({ level, msg: objOrMsg }))
+    } else {
+      fn(JSON.stringify({ level, ...objOrMsg, msg: msg ?? (objOrMsg as { msg?: string }).msg }))
+    }
+  }
+
+const cloudflareLogger = {
+  level: process.env.PAYLOAD_LOG_LEVEL || 'info',
+  trace: createLog('trace', console.debug),
+  debug: createLog('debug', console.debug),
+  info: createLog('info', console.log),
+  warn: createLog('warn', console.warn),
+  error: createLog('error', console.error),
+  fatal: createLog('fatal', console.error),
+  silent: () => {},
+} as any // Use PayloadLogger type when it's exported
+
 const cloudflare =
   isCLI || !isProduction
     ? await getCloudflareContextFromWrangler()
@@ -37,6 +57,7 @@ export default buildConfig({
     outputFile: path.resolve(dirname, 'payload-types.ts'),
   },
   db: sqliteD1Adapter({ binding: cloudflare.env.D1 }),
+  logger: isProduction ? cloudflareLogger : undefined,
   plugins: [
     r2Storage({
       bucket: cloudflare.env.R2,

PATCH

echo "Patch applied successfully."

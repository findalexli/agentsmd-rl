#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-plugins-plus-skills

# Idempotency guard
if grep -qF "Configure Sentry for local development with environment-aware DSN routing, debug" "plugins/saas-packs/sentry-pack/skills/sentry-local-dev-loop/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/saas-packs/sentry-pack/skills/sentry-local-dev-loop/SKILL.md b/plugins/saas-packs/sentry-pack/skills/sentry-local-dev-loop/SKILL.md
@@ -1,222 +1,431 @@
 ---
 name: sentry-local-dev-loop
 description: |
-  Set up local development workflow with Sentry.
-  Use when configuring Sentry for development environments,
-  setting up debug mode, or testing error capture locally.
-  Trigger with phrases like "sentry local dev", "sentry development",
-  "debug sentry", "sentry dev environment".
-allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(node:*), Grep
+  Configure Sentry for local development with environment-aware settings.
+  Use when setting up dev vs prod DSN routing, enabling debug mode,
+  tuning sample rates for local work, or testing source maps locally.
+  Trigger with phrases like "sentry local dev", "sentry development config",
+  "debug sentry locally", "sentry dev environment", "sentry spotlight".
+allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(node:*), Bash(npx:*), Bash(python:*), Grep, Glob
 version: 1.0.0
 license: MIT
 author: Jeremy Longshore <jeremy@intentsolutions.io>
 compatible-with: claude-code, codex, openclaw
-tags: [saas, sentry, testing, debugging, workflow, development]
+tags: [saas, sentry, development, debugging, workflow, devtools, environment]
 
 ---
 # Sentry Local Dev Loop
 
+## Overview
+
+Configure Sentry for local development with environment-aware DSN routing, debug-mode verbosity, full-capture sample rates, `beforeSend` inspection, Sentry Spotlight for offline event viewing, and `sentry-cli` source map verification. All configuration uses environment variables so nothing leaks into commits.
+
 ## Prerequisites
-- Sentry SDK installed
-- Separate Sentry project for development (recommended)
-- `.env` file with development DSN
+
+- `@sentry/node` v8+ installed (TypeScript/Node) or `sentry-sdk` v2+ installed (Python)
+- Separate Sentry project created for development (different DSN from production)
+- `.env` file with `SENTRY_DSN_DEV` and `NODE_ENV=development`
+- Network access to `*.ingest.sentry.io` (or use Spotlight for fully offline work)
 
 ## Instructions
 
-### 1. Development-Optimized Sentry.init
+### Step 1 -- Environment-Aware Configuration
+
+Create an initialization file that routes events to the correct Sentry project based on environment, enables debug logging in dev, and captures 100% of traces locally:
 
 ```typescript
-// instrument.dev.mjs — development configuration
+// instrument.mjs — import via: node --import ./instrument.mjs app.mjs
 import * as Sentry from '@sentry/node';
 
-const isDev = process.env.NODE_ENV !== 'production';
+const env = process.env.NODE_ENV || 'development';
+const isDev = env !== 'production';
 
 Sentry.init({
-  dsn: isDev ? process.env.SENTRY_DSN_DEV : process.env.SENTRY_DSN,
-
-  environment: 'development',
-  release: 'dev-local',
-
-  // Capture everything in development
-  tracesSampleRate: 1.0,
-  sampleRate: 1.0,
-
-  // Enable verbose logging to console
-  debug: true,
-
-  // Include default PII in dev for easier debugging
-  sendDefaultPii: true,
-
-  // Optional: disable sending to Sentry entirely for offline work
-  // dsn: '', // Empty DSN = SDK initialized but no events sent
+  // Route to dev project locally, prod project in production
+  dsn: isDev
+    ? process.env.SENTRY_DSN_DEV
+    : process.env.SENTRY_DSN,
+
+  environment: env,
+  release: isDev ? 'dev-local' : process.env.SENTRY_RELEASE,
+
+  // Full capture in dev — you need every event for debugging
+  tracesSampleRate: isDev ? 1.0 : 0.1,
+  sampleRate: isDev ? 1.0 : 1.0,
+
+  // Verbose SDK output to console in dev
+  debug: isDev,
+
+  // Include PII locally for easier debugging (never in prod)
+  sendDefaultPii: isDev,
+
+  // Sentry Spotlight — shows events in local browser UI
+  // Install: npx @spotlightjs/spotlight
+  spotlight: isDev,
+
+  beforeSend(event, hint) {
+    if (isDev) {
+      const exc = event.exception?.values?.[0];
+      const label = exc
+        ? `${exc.type}: ${exc.value}`
+        : event.message || 'event';
+      console.log(`[Sentry Dev] ${label}`);
+      console.log(`  Tags: ${JSON.stringify(event.tags || {})}`);
+    }
+    return event;
+  },
 
-  beforeSend(event) {
-    // In dev, also log to console for immediate feedback
-    console.log('[Sentry Event]', event.exception?.values?.[0]?.value || event.message);
+  beforeSendTransaction(event) {
+    if (isDev) {
+      const duration = event.timestamp && event.start_timestamp
+        ? ((event.timestamp - event.start_timestamp) * 1000).toFixed(0)
+        : '?';
+      console.log(`[Sentry Dev] Transaction: ${event.transaction} (${duration}ms)`);
+    }
     return event;
   },
 });
 ```
 
-### 2. Environment Variable Setup
+Set up environment files to keep DSNs out of source:
 
 ```bash
 # .env.development
-SENTRY_DSN_DEV=https://dev-key@o0.ingest.sentry.io/dev-project
+SENTRY_DSN_DEV=https://examplePublicKey@o0.ingest.sentry.io/0
 SENTRY_ENVIRONMENT=development
-SENTRY_RELEASE=dev-local
 NODE_ENV=development
 
 # .env.production
-SENTRY_DSN=https://prod-key@o0.ingest.sentry.io/prod-project
+SENTRY_DSN=https://prodPublicKey@o0.ingest.sentry.io/0
 SENTRY_ENVIRONMENT=production
+SENTRY_RELEASE=v1.2.3
 NODE_ENV=production
 ```
 
-### 3. Conditional Initialization Pattern
-
-```typescript
-// lib/sentry.ts — environment-aware initialization
-import * as Sentry from '@sentry/node';
-
-export function initSentry() {
-  const env = process.env.NODE_ENV || 'development';
-
-  // Option A: Skip Sentry entirely in dev
-  if (env === 'development' && !process.env.SENTRY_DSN_DEV) {
-    console.log('[Sentry] Skipped — no dev DSN configured');
-    return;
-  }
-
-  // Option B: Initialize with dev-specific settings
-  Sentry.init({
-    dsn: env === 'development'
-      ? process.env.SENTRY_DSN_DEV
-      : process.env.SENTRY_DSN,
-    environment: env,
-    debug: env === 'development',
-    tracesSampleRate: env === 'development' ? 1.0 : 0.1,
-    sendDefaultPii: env === 'development',
+Add DSN safety to `.gitignore`:
 
-    // In dev, also log events to console
-    beforeSend(event) {
-      if (env === 'development') {
-        const errorType = event.exception?.values?.[0]?.type;
-        const errorMsg = event.exception?.values?.[0]?.value;
-        console.log(`[Sentry] ${errorType}: ${errorMsg}`);
-      }
-      return event;
-    },
-  });
-}
+```gitignore
+.env
+.env.development
+.env.production
+.env.local
 ```
 
-### 4. Local Verification Script
+### Step 2 -- Local Verification and Performance Debugging
+
+Create a verification script that confirms the SDK works end-to-end and demonstrates `Sentry.startSpan()` for local performance profiling:
 
 ```typescript
-// scripts/verify-sentry.mjs
+// scripts/verify-sentry.mjs — run: node --import ./instrument.mjs scripts/verify-sentry.mjs
 import * as Sentry from '@sentry/node';
 
-Sentry.init({
-  dsn: process.env.SENTRY_DSN_DEV || process.env.SENTRY_DSN,
-  debug: true,
-  environment: 'verification',
-});
-
 async function verify() {
-  console.log('1. Testing captureMessage...');
-  Sentry.captureMessage('Dev verification test', 'info');
+  const client = Sentry.getClient();
+  if (!client) {
+    console.error('Sentry SDK not initialized — run with --import ./instrument.mjs');
+    process.exit(1);
+  }
+  console.log('--- Sentry Dev Loop Verification ---\n');
+
+  // 1. Test captureMessage
+  console.log('1. Sending test message...');
+  Sentry.captureMessage('Dev loop verification — captureMessage', 'info');
 
-  console.log('2. Testing captureException...');
+  // 2. Test captureException
+  console.log('2. Sending test exception...');
   try {
-    throw new Error('Dev loop verification error');
+    throw new Error('Dev loop verification — captureException');
   } catch (e) {
-    Sentry.captureException(e);
+    const eventId = Sentry.captureException(e);
+    console.log(`   Event ID: ${eventId}`);
   }
 
-  console.log('3. Testing performance span...');
+  // 3. Test Sentry.startSpan for local performance profiling
+  console.log('3. Testing startSpan for performance...');
   await Sentry.startSpan(
-    { name: 'dev.verification', op: 'test' },
-    async () => {
-      await new Promise((r) => setTimeout(r, 100));
+    { name: 'dev.verification.database', op: 'db.query' },
+    async (span) => {
+      // Simulate a slow database query
+      await new Promise((resolve) => setTimeout(resolve, 150));
+
+      // Nested span for a sub-operation
+      await Sentry.startSpan(
+        { name: 'dev.verification.serialize', op: 'serialize' },
+        async () => {
+          await new Promise((resolve) => setTimeout(resolve, 50));
+        }
+      );
     }
   );
 
-  console.log('4. Flushing events...');
+  // 4. Test breadcrumb trail
+  console.log('4. Testing breadcrumbs...');
+  Sentry.addBreadcrumb({
+    category: 'dev',
+    message: 'Verification script started',
+    level: 'info',
+  });
+  Sentry.addBreadcrumb({
+    category: 'dev',
+    message: 'All checks passed',
+    level: 'info',
+  });
+  Sentry.captureMessage('Dev verification complete with breadcrumbs', 'info');
+
+  // 5. Flush — critical for scripts that exit immediately
+  console.log('5. Flushing events...');
   const flushed = await Sentry.flush(5000);
-  console.log(flushed ? 'All events sent' : 'Flush timed out — check DSN');
+  console.log(flushed
+    ? '\nAll events sent — check Sentry dashboard or Spotlight UI'
+    : '\nFlush timed out — check DSN and network'
+  );
 }
 
 verify();
 ```
 
-### 5. Sentry Spotlight for Local Debugging
+Use `Sentry.startSpan()` in your application code to profile specific operations during development:
 
-Sentry Spotlight is a dev tool that shows Sentry events in your browser without sending to sentry.io:
+```typescript
+// Profile a real endpoint handler locally
+app.get('/api/search', async (req, res) => {
+  const results = await Sentry.startSpan(
+    { name: 'search.execute', op: 'db.query', attributes: { 'search.query': req.query.q } },
+    async () => {
+      return await db.search(req.query.q);
+    }
+  );
+
+  const formatted = await Sentry.startSpan(
+    { name: 'search.format', op: 'serialize' },
+    async () => {
+      return results.map(formatResult);
+    }
+  );
+
+  res.json(formatted);
+});
+```
+
+### Step 3 -- Sentry Spotlight and Offline Development
+
+Sentry Spotlight runs a local sidecar that intercepts Sentry events and displays them in a browser UI at `http://localhost:8969` (Spotlight's default port) — no network required:
 
 ```bash
-# Install Spotlight sidecar
+# Install and run Spotlight sidecar (runs alongside your dev server)
 npx @spotlightjs/spotlight
 ```
 
-```typescript
-// instrument.dev.mjs — with Spotlight
-import * as Sentry from '@sentry/node';
-import { setupSidecar } from '@spotlightjs/sidecar';
+The `spotlight: true` option in Step 1's `Sentry.init()` routes events to the local sidecar. This gives you a full Sentry-style event viewer without sending anything to `sentry.io`.
+
+For fully offline development or CI environments with no Sentry access:
 
+```typescript
+// Offline mode — SDK loads but sends nothing
 Sentry.init({
-  dsn: process.env.SENTRY_DSN_DEV,
-  debug: true,
-  spotlight: process.env.NODE_ENV === 'development',
-  // Spotlight intercepts events and shows them in a local UI
-  // at http://localhost:8969/stream
+  dsn: '',        // Empty DSN = all capture calls become no-ops
+  debug: false,   // No debug output since nothing is sent
 });
+
+// All Sentry.captureException() and captureMessage() calls still work
+// without throwing — your code runs without modification
+```
+
+Test source maps locally before deploying with `sentry-cli`:
+
+```bash
+# Install sentry-cli
+npm install -g @sentry/cli
+
+# Verify authentication
+sentry-cli info
+
+# Upload source maps for a test release
+sentry-cli sourcemaps upload \
+  --org your-org \
+  --project your-dev-project \
+  --release dev-local \
+  ./dist
+
+# Verify source maps are correctly linked
+sentry-cli sourcemaps explain \
+  --org your-org \
+  --project your-dev-project \
+  --release dev-local
 ```
 
-### 6. Git Hook for Pre-Push Verification
+Add a git pre-push hook to prevent hardcoded DSNs from leaking into the repo:
 
 ```bash
 #!/bin/bash
-# .git/hooks/pre-push — verify Sentry doesn't have hardcoded DSNs
-if grep -r "ingest.sentry.io" --include="*.ts" --include="*.js" \
-   --exclude-dir=node_modules --exclude-dir=dist src/; then
-  echo "ERROR: Hardcoded Sentry DSN found. Use environment variables."
+set -e
+# .git/hooks/pre-push — block commits with hardcoded DSNs
+if grep -rn "ingest\.sentry\.io" --include="*.ts" --include="*.js" \
+   --exclude-dir=node_modules --exclude-dir=dist src/ lib/; then
+  echo "ERROR: Hardcoded Sentry DSN found in source. Use environment variables."
   exit 1
 fi
 ```
 
-### 7. Testing Without Network
+## Output
+
+- Environment-aware `Sentry.init()` routing dev events to a separate Sentry project
+- Debug logging printing captured events and transaction durations to the console
+- Verification script confirming captureMessage, captureException, and startSpan work
+- Sentry Spotlight integration for browsing events locally without network
+- Source map upload and verification workflow with `sentry-cli`
+- Pre-push hook preventing hardcoded DSNs from entering version control
+
+## Error Handling
+
+| Error | Cause | Solution |
+|-------|-------|----------|
+| Events going to prod project | Wrong DSN loaded for environment | Verify `SENTRY_DSN_DEV` is set; log `process.env.NODE_ENV` at startup |
+| Debug output too verbose | `debug: true` left on in production | Gate with `debug: isDev` as shown in Step 1 |
+| Events not appearing in Spotlight | Sidecar not running | Run `npx @spotlightjs/spotlight` in a separate terminal |
+| `Sentry.flush()` times out | No network or invalid DSN | Check DSN, test with `curl https://sentry.io/api/0/` |
+| Rate-limited during dev | 100% sample rate hitting project quota | Use a dedicated dev project with separate quota |
+| Source maps not resolving | Release mismatch between upload and init | Ensure `--release` in `sentry-cli` matches `release` in `Sentry.init()` |
+| `getClient()` returns undefined | SDK not initialized before check | Import `instrument.mjs` via `--import` flag before any app code |
+| `beforeSend` dropping events | Returns `undefined` instead of event | Always return `event` to keep it, or `null` to explicitly drop |
+
+## Examples
+
+### TypeScript — Conditional Init Helper
 
 ```typescript
-// For offline development or CI without Sentry access:
-Sentry.init({
-  dsn: '', // Empty DSN = SDK loads but sends nothing
-  debug: false,
-});
+// lib/sentry.ts — reusable initialization for any Node.js app
+import * as Sentry from '@sentry/node';
+
+export function initSentry() {
+  const env = process.env.NODE_ENV || 'development';
+  const isDev = env !== 'production';
+
+  // Option A: Skip Sentry entirely if no dev DSN is configured
+  if (isDev && !process.env.SENTRY_DSN_DEV) {
+    console.log('[Sentry] Skipped — no SENTRY_DSN_DEV configured');
+    return;
+  }
+
+  Sentry.init({
+    dsn: isDev ? process.env.SENTRY_DSN_DEV : process.env.SENTRY_DSN,
+    environment: env,
+    debug: isDev,
+    tracesSampleRate: isDev ? 1.0 : 0.1,
+    spotlight: isDev,
+    sendDefaultPii: isDev,
+
+    beforeSend(event) {
+      if (isDev) {
+        const exc = event.exception?.values?.[0];
+        console.log(`[Sentry] ${exc?.type || 'Event'}: ${exc?.value || event.message}`);
+      }
+      return event;
+    },
+  });
 
-// All Sentry.captureException() calls become no-ops
-// Your app code continues working without modification
+  console.log(`[Sentry] Initialized for ${env}`);
+}
 ```
 
-## Output
-- Environment-aware Sentry configuration switching dev/prod
-- Debug logging enabled showing events in console during dev
-- Verification script confirming SDK works end-to-end
-- Spotlight integration for local event inspection
-- DSN security check preventing hardcoded secrets in commits
+### Python — Environment-Aware Setup
 
-## Error Handling
+```python
+# sentry_config.py — environment-aware initialization
+import os
+import sentry_sdk
 
-| Error | Cause | Solution |
-|-------|-------|----------|
-| Events going to prod project | Wrong DSN loaded | Use separate `SENTRY_DSN_DEV` and verify `NODE_ENV` |
-| Debug output too verbose | `debug: true` in production | Gate debug mode behind environment check |
-| Events not appearing locally | Firewall blocking sentry.io | Use Spotlight for local dev, or set `dsn: ''` for offline |
-| Rate-limited during dev | `tracesSampleRate: 1.0` sending too many events | Use separate dev project with its own quota |
-| `Sentry.flush()` times out | No network or invalid DSN | Check DSN, verify network with `curl https://sentry.io/api/0/` |
+def init_sentry():
+    env = os.getenv("SENTRY_ENVIRONMENT", "development")
+    is_dev = env != "production"
+
+    dsn = (
+        os.getenv("SENTRY_DSN_DEV")
+        if is_dev
+        else os.getenv("SENTRY_DSN")
+    )
+
+    if is_dev and not dsn:
+        print("[Sentry] Skipped — no SENTRY_DSN_DEV configured")
+        return
+
+    sentry_sdk.init(
+        dsn=dsn,
+        environment=env,
+        release="dev-local" if is_dev else os.getenv("SENTRY_RELEASE"),
+
+        # Full capture in dev
+        traces_sample_rate=1.0 if is_dev else 0.1,
+        sample_rate=1.0,
+
+        # Verbose SDK logging in dev
+        debug=is_dev,
+
+        # Sentry Spotlight for local event viewing
+        spotlight=True if is_dev else False,
+
+        # Inspect events before they are sent
+        before_send=_before_send_dev if is_dev else None,
+    )
+
+    print(f"[Sentry] Initialized for {env}")
+
+
+def _before_send_dev(event, hint):
+    """Log events to console during local development."""
+    exc_info = hint.get("exc_info")
+    if exc_info:
+        exc_type, exc_value, _ = exc_info
+        print(f"[Sentry Dev] {exc_type.__name__}: {exc_value}")
+    elif event.get("message"):
+        print(f"[Sentry Dev] Message: {event['message']}")
+    return event
+```
+
+```python
+# verify_sentry.py — verification script
+import os
+import sentry_sdk
+
+sentry_sdk.init(
+    dsn=os.getenv("SENTRY_DSN_DEV"),
+    debug=True,
+    environment="verification",
+    spotlight=True,
+)
+
+# Test captureMessage
+sentry_sdk.capture_message("Dev verification — Python", "info")
+
+# Test captureException
+try:
+    raise ValueError("Dev verification error — Python")
+except Exception as e:
+    event_id = sentry_sdk.capture_exception(e)
+    print(f"Event ID: {event_id}")
+
+# Test performance span
+with sentry_sdk.start_span(op="test", description="verification span"):
+    import time
+    time.sleep(0.1)
+
+sentry_sdk.flush()
+print("Verification complete — check Sentry dashboard or Spotlight")
+```
 
 ## Resources
-- [Configuration Options](https://docs.sentry.io/platforms/javascript/configuration/options/)
-- [Environments](https://docs.sentry.io/platforms/javascript/configuration/environments/)
-- [Sentry Spotlight](https://spotlightjs.com/)
-- [Debug Mode](https://docs.sentry.io/platforms/javascript/configuration/options/#debug)
+
+- [Configuration Options](https://docs.sentry.io/platforms/javascript/configuration/options/) -- all `Sentry.init()` options reference
+- [Environments](https://docs.sentry.io/platforms/javascript/configuration/environments/) -- environment tagging
+- [Debug Mode](https://docs.sentry.io/platforms/javascript/configuration/options/#debug) -- verbose SDK logging
+- [Sentry Spotlight](https://spotlightjs.com/) -- local event viewer
+- [Source Maps with sentry-cli](https://docs.sentry.io/platforms/javascript/sourcemaps/uploading/cli/) -- upload and verify source maps
+- [Performance Instrumentation](https://docs.sentry.io/platforms/javascript/tracing/instrumentation/custom-instrumentation/) -- `startSpan()` API
+- [Python SDK Configuration](https://docs.sentry.io/platforms/python/configuration/options/) -- Python `sentry_sdk.init()` options
+
+## Next Steps
+
+- **sentry-multi-env-setup** -- Extend to staging, canary, and multi-region environment routing
+- **sentry-performance-tracing** -- Production-grade tracing with custom spans and distributed traces
+- **sentry-debug-bundle** -- Advanced debugging with session replay and profiling
+- **sentry-ci-integration** -- Automate source map uploads and release creation in CI/CD
PATCH

echo "Gold patch applied."

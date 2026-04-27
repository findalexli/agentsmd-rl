#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-plugins-plus-skills

# Idempotency guard
if grep -qF "Capture errors and enrich them with structured context so your team can diagnose" "plugins/saas-packs/sentry-pack/skills/sentry-error-capture/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/saas-packs/sentry-pack/skills/sentry-error-capture/SKILL.md b/plugins/saas-packs/sentry-pack/skills/sentry-error-capture/SKILL.md
@@ -2,49 +2,85 @@
 name: sentry-error-capture
 description: |
   Implement advanced error capture and context enrichment with Sentry.
-  Use when implementing detailed error tracking, adding context,
-  or customizing error capture behavior.
-  Trigger with phrases like "sentry error capture", "sentry context",
-  "enrich sentry errors", "sentry exception handling".
-allowed-tools: Read, Write, Edit, Grep, Bash(node:*)
+  Use when adding captureException/captureMessage calls, enriching errors
+  with user context, tags, breadcrumbs, or custom fingerprinting.
+  Trigger with "sentry error capture", "sentry context", "enrich sentry errors",
+  "sentry exception handling", "sentry breadcrumbs", "sentry fingerprint".
+allowed-tools: Read, Write, Edit, Grep, Glob, Bash(npm:*), Bash(npx:*), Bash(pip:*), Bash(python:*)
 version: 1.0.0
 license: MIT
 author: Jeremy Longshore <jeremy@intentsolutions.io>
 compatible-with: claude-code, codex, openclaw
-tags: [saas, sentry, error-tracking, context, breadcrumbs]
-
+tags: [saas, sentry, error-tracking, context, breadcrumbs, observability]
 ---
+
 # Sentry Error Capture
 
+## Overview
+
+Capture errors and enrich them with structured context so your team can diagnose production issues in seconds instead of hours. Covers `captureException`, `captureMessage`, scoped context (`withScope` / `push_scope`), breadcrumbs, custom fingerprinting, and `beforeSend` filtering using `@sentry/node` v8 and `sentry-sdk` v2 APIs.
+
 ## Prerequisites
-- Sentry SDK v8 installed and initialized
-- Understanding of try/catch and async error handling
-- Application logging infrastructure in place
+
+- Sentry SDK installed and initialized (`@sentry/node` v8+ or `sentry-sdk` v2+)
+- A valid DSN configured via environment variable (`SENTRY_DSN`)
+- Understanding of try/catch (JS) or try/except (Python) error handling
+- A Sentry project created at [sentry.io](https://sentry.io)
 
 ## Instructions
 
-### 1. captureException — The Core Method
+### Step 1 -- Capture Exceptions with Full Stack Traces
 
-Always pass real `Error` objects, never plain strings:
+Always pass real `Error` objects (or Python exception instances), never plain strings. Plain strings lose the stack trace, making debugging far harder.
+
+**TypeScript (`@sentry/node`)**
 
 ```typescript
 import * as Sentry from '@sentry/node';
 
-// CORRECT — full stack trace preserved
+// CORRECT -- full stack trace preserved
 try {
   await riskyOperation();
 } catch (error) {
   Sentry.captureException(error);
 }
 
-// WRONG — no stack trace, hard to debug
+// WRONG -- no stack trace, hard to debug
 Sentry.captureException('something went wrong');
 
-// Wrapping non-Error values
+// Wrapping non-Error values into proper Error objects
 Sentry.captureException(new Error(`API returned ${statusCode}: ${body}`));
+
+// Capture with inline context (no scope needed for simple cases)
+Sentry.captureException(error, {
+  tags: { transaction: 'purchase' },
+  extra: { orderId, amount },
+});
 ```
 
-### 2. captureMessage — For Informational Events
+**Python (`sentry-sdk`)**
+
+```python
+import sentry_sdk
+
+# CORRECT -- full traceback preserved
+try:
+    risky_operation()
+except Exception as e:
+    sentry_sdk.capture_exception(e)
+
+# Capture current exception implicitly (inside except block)
+try:
+    risky_operation()
+except Exception:
+    sentry_sdk.capture_exception()  # captures sys.exc_info() automatically
+```
+
+### Step 2 -- Capture Messages for Non-Exception Events
+
+Use `captureMessage` for events that are not exceptions but still worth tracking: deprecation warnings, capacity thresholds, business logic anomalies.
+
+**TypeScript**
 
 ```typescript
 // Severity levels: 'fatal' | 'error' | 'warning' | 'info' | 'debug' | 'log'
@@ -53,84 +89,136 @@ Sentry.captureMessage('Deprecated API endpoint accessed', 'warning');
 Sentry.captureMessage('Database connection pool exhausted', 'fatal');
 ```
 
-### 3. Scoped Context with withScope
+**Python**
+
+```python
+sentry_sdk.capture_message("Payment gateway timeout", level="warning")
+sentry_sdk.capture_message("Daily report generated", level="info")
+sentry_sdk.capture_message("Connection pool exhausted", level="fatal")
+```
+
+### Step 3 -- Enrich Events with Scoped Context
+
+Use `withScope` (TypeScript) or `push_scope` (Python) to attach context to a single event without polluting the global scope. Context is automatically cleaned up when the scope exits.
 
-Use `withScope` to attach context to a single event without polluting the global scope:
+**TypeScript -- withScope**
 
 ```typescript
 Sentry.withScope((scope) => {
+  // User identity for issue assignment and impact analysis
+  scope.setUser({
+    id: user.id,
+    email: user.email,
+    subscription: user.plan,
+  });
+
+  // Tags: indexed, searchable in Sentry UI filters
   scope.setTag('payment_provider', 'stripe');
-  scope.setTag('payment_type', 'subscription');
-  scope.setLevel('error');
+  scope.setTag('feature', 'checkout');
 
+  // Structured context: visible in event detail sidebar
   scope.setContext('payment', {
     amount: 9999,
     currency: 'USD',
     customer_id: 'cus_abc123',
     idempotency_key: 'idem_xyz789',
   });
 
-  scope.setUser({
-    id: user.id,
-    email: user.email,
-    subscription: user.plan,
-  });
+  // Extra data: arbitrary key-value pairs for debugging
+  scope.setExtra('cart', cartItems);
+
+  // Override severity level
+  scope.setLevel('fatal');
 
-  scope.setFingerprint(['payment-failure', paymentProvider]);
+  // Custom fingerprint to control issue grouping
+  scope.setFingerprint(['checkout-failure', paymentProvider]);
 
   Sentry.captureException(error);
 });
-// Scope is automatically cleaned up — global scope unchanged
+// Scope is automatically cleaned up -- global scope unchanged
+```
+
+**Python -- push_scope**
+
+```python
+with sentry_sdk.push_scope() as scope:
+    scope.user = {"id": user_id, "email": user_email}
+    scope.set_tag("feature", "checkout")
+    scope.set_extra("cart", cart_items)
+    scope.level = "fatal"
+    scope.fingerprint = ["checkout-failure", str(error_code)]
+    sentry_sdk.capture_exception(error)
+# Scope is automatically cleaned up
 ```
 
-### 4. Breadcrumbs for Debugging Context
+## Breadcrumbs
 
-Breadcrumbs create a trail of events leading up to an error:
+Breadcrumbs create a trail of events leading up to an error. Sentry auto-captures some (console logs, HTTP requests, DOM events), but manual breadcrumbs add domain-specific context.
+
+**TypeScript**
 
 ```typescript
-// Manual breadcrumbs
 Sentry.addBreadcrumb({
   category: 'auth',
   message: `User ${userId} logged in via ${provider}`,
   level: 'info',
   data: { provider, method: 'oauth2' },
 });
 
-Sentry.addBreadcrumb({
-  category: 'navigation',
-  message: 'User navigated to /checkout',
-  level: 'info',
-});
-
 Sentry.addBreadcrumb({
   category: 'transaction',
   message: 'Payment initiated',
   level: 'info',
   data: { amount: 49.99, items: 3 },
 });
-
 // The next captured error includes all breadcrumbs above
 ```
 
-### 5. Custom Fingerprinting for Issue Grouping
+**Python**
+
+```python
+sentry_sdk.add_breadcrumb(
+    category="auth",
+    message=f"User {user_id} logged in via {provider}",
+    level="info",
+    data={"provider": provider, "method": "oauth2"},
+)
+
+sentry_sdk.add_breadcrumb(
+    category="transaction",
+    message="Payment initiated",
+    level="info",
+    data={"amount": 49.99, "items": 3},
+)
+```
 
-Override Sentry's default grouping to control how errors are grouped into issues:
+## Custom Fingerprinting
+
+Override Sentry's default grouping to control how errors are merged into issues. Without custom fingerprints, Sentry groups by stack trace, which can split logically identical errors or merge unrelated ones.
 
 ```typescript
+// Group all timeout errors for /api/search into one issue
 Sentry.withScope((scope) => {
-  // Group all timeout errors for /api/search into one issue
   scope.setFingerprint(['api-timeout', 'search-endpoint']);
   Sentry.captureException(new Error('Search API timeout'));
 });
 
-// Group by error type + HTTP status
+// Group by error type + HTTP status + endpoint
 Sentry.withScope((scope) => {
   scope.setFingerprint(['http-error', String(response.status), endpoint]);
   Sentry.captureException(error);
 });
+
+// Use {{ default }} to extend rather than replace default grouping
+Sentry.withScope((scope) => {
+  scope.setFingerprint(['{{ default }}', tenantId]);
+  Sentry.captureException(error);
+});
 ```
 
-### 6. beforeSend for Global Filtering and Enrichment
+## Global Filtering with beforeSend
+
+Configure `beforeSend` during initialization to filter noise, scrub sensitive data, or enrich all events globally.
 
 ```typescript
 Sentry.init({
@@ -142,13 +230,13 @@ Sentry.init({
     if (error instanceof AbortError) return null;
     if (error?.message?.match(/ResizeObserver loop/)) return null;
 
-    // Scrub sensitive data from event
+    // Scrub sensitive headers
     if (event.request?.headers) {
       delete event.request.headers['Authorization'];
       delete event.request.headers['Cookie'];
     }
 
-    // Add custom context based on error type
+    // Enrich database errors with subsystem tag
     if (error instanceof DatabaseError) {
       event.tags = { ...event.tags, subsystem: 'database' };
       event.level = 'fatal';
@@ -157,7 +245,7 @@ Sentry.init({
     return event; // Must return event or null
   },
 
-  // Filter noisy errors by pattern
+  // Pattern-based noise filtering
   ignoreErrors: [
     'ResizeObserver loop',
     'Non-Error promise rejection',
@@ -167,21 +255,38 @@ Sentry.init({
 });
 ```
 
-### 7. Express Error Handler
+## Output
+
+- Errors with full stack traces and context in the Sentry Issues dashboard
+- Scoped tags and structured context for filtering and search
+- Breadcrumb trails showing the user journey before errors
+- Custom fingerprints grouping related errors into single issues
+- Clean event stream via `beforeSend` filtering and `ignoreErrors`
+
+## Error Handling
+
+| Error | Cause | Solution |
+|-------|-------|----------|
+| Missing stack trace | String passed instead of Error object | Always use `new Error()` or extend the Error class |
+| Events not grouped properly | Default fingerprinting insufficient | Use `scope.setFingerprint()` with domain-specific keys |
+| `beforeSend` dropping all events | Function returns `undefined` | Always return `event` or explicitly `null` |
+| Scope leaking between requests | Global scope modified in async context | Use `withScope()` / `push_scope()` for per-request context |
+| Too many events hitting quota | No filtering or sampling configured | Add `ignoreErrors`, `beforeSend` filters, or `sampleRate` |
+| Context not showing in Sentry UI | Used `setExtra` for structured data | Use `setContext('name', {...})` for sidebar visibility |
+
+## Examples
+
+### TypeScript -- Express Route with Context
 
 ```typescript
 import express from 'express';
 import * as Sentry from '@sentry/node';
 
 const app = express();
-
-// Sentry request handler — must be first middleware
 Sentry.setupExpressErrorHandler(app);
 
-// Your routes
 app.get('/api/users/:id', async (req, res) => {
   Sentry.setUser({ id: req.params.id });
-
   try {
     const user = await getUser(req.params.id);
     res.json(user);
@@ -199,20 +304,17 @@ app.get('/api/users/:id', async (req, res) => {
 });
 ```
 
-### 8. Async Error Handling
+### TypeScript -- Batch Processing with Promise.allSettled
 
 ```typescript
-// Promise rejections — Sentry captures unhandled rejections automatically
-// For handled promises, capture explicitly:
 async function processQueue(items: QueueItem[]) {
   const results = await Promise.allSettled(
     items.map(item => processItem(item))
   );
-
   results.forEach((result, index) => {
     if (result.status === 'rejected') {
       Sentry.withScope((scope) => {
-        scope.setTag('queue_item_index', index);
+        scope.setTag('queue_item_index', String(index));
         scope.setContext('item', items[index]);
         Sentry.captureException(result.reason);
       });
@@ -221,59 +323,44 @@ async function processQueue(items: QueueItem[]) {
 }
 ```
 
-### 9. Domain-Specific Error Classes
-
-```typescript
-class AppError extends Error {
-  constructor(
-    message: string,
-    public code: string,
-    public severity: Sentry.SeverityLevel = 'error',
-    public context?: Record<string, unknown>
-  ) {
-    super(message);
-    this.name = 'AppError';
-  }
-}
-
-function captureAppError(error: AppError) {
-  Sentry.withScope((scope) => {
-    scope.setTag('error_code', error.code);
-    scope.setLevel(error.severity);
-    if (error.context) {
-      scope.setContext('app_error', error.context);
-    }
-    Sentry.captureException(error);
-  });
-}
-
-// Usage
-throw new AppError('Insufficient funds', 'PAYMENT_001', 'warning', {
-  balance: 10.00,
-  required: 49.99,
-});
+### Python -- Background Job Error
+
+```python
+import sentry_sdk
+
+def process_report(report_id: str, user_id: str):
+    sentry_sdk.add_breadcrumb(
+        category="jobs",
+        message=f"Report generation started: {report_id}",
+        level="info",
+    )
+    try:
+        data = fetch_report_data(report_id)
+        return generate_pdf(data)
+    except Exception as error:
+        with sentry_sdk.push_scope() as scope:
+            scope.user = {"id": user_id}
+            scope.set_tag("job_type", "report_generation")
+            scope.set_context("report", {
+                "report_id": report_id,
+                "stage": "pdf_generation",
+            })
+            scope.fingerprint = ["report-failure", report_id]
+            sentry_sdk.capture_exception(error)
+        raise
 ```
 
-## Output
-- Errors with full stack traces and context in Sentry dashboard
-- Scoped tags and context for filtering and search
-- Breadcrumb trails showing user actions before errors
-- Custom fingerprinting grouping related errors into single issues
-- Clean error filtering via beforeSend and ignoreErrors
+## Resources
 
-## Error Handling
+- [Capturing Errors](https://docs.sentry.io/platforms/javascript/usage/) -- `captureException` and `captureMessage` reference
+- [Scopes and Context](https://docs.sentry.io/platforms/javascript/enriching-events/scopes/) -- `withScope`, `setUser`, `setTag`, `setContext`
+- [Breadcrumbs](https://docs.sentry.io/platforms/javascript/enriching-events/breadcrumbs/) -- manual and auto-captured breadcrumbs
+- [Filtering Events](https://docs.sentry.io/platforms/javascript/configuration/filtering/) -- `beforeSend`, `ignoreErrors`, sampling
+- [Issue Grouping](https://docs.sentry.io/product/data-management-settings/event-grouping/) -- fingerprinting and merge/unmerge
+- [Python SDK Usage](https://docs.sentry.io/platforms/python/usage/) -- Python-specific capture patterns
 
-| Error | Cause | Solution |
-|-------|-------|----------|
-| Missing stack trace | String passed instead of Error object | Always use `new Error()` or extend Error class |
-| Events not grouped properly | Default fingerprinting insufficient | Use `scope.setFingerprint()` for custom grouping |
-| `beforeSend` dropping all events | Function returns `undefined` instead of event | Ensure `beforeSend` always returns `event` or explicitly `null` |
-| Scope leaking between requests | Using global scope in async context | Use `withScope()` for per-request context |
-| Too many events | No filtering configured | Add `ignoreErrors`, `beforeSend` filters, or `sampleRate` |
+## Next Steps
 
-## Resources
-- [Capturing Errors](https://docs.sentry.io/platforms/javascript/usage/)
-- [Scopes & Context](https://docs.sentry.io/platforms/javascript/enriching-events/scopes/)
-- [Breadcrumbs](https://docs.sentry.io/platforms/javascript/enriching-events/breadcrumbs/)
-- [Filtering Events](https://docs.sentry.io/platforms/javascript/configuration/filtering/)
-- [Issue Grouping](https://docs.sentry.io/product/data-management-settings/event-grouping/)
+- **Performance tracing**: Add `Sentry.startSpan()` to measure operation timing (see `sentry-performance-tracing`)
+- **Release management**: Tag errors with release versions for regression detection (see `sentry-release-management`)
+- **Cost tuning**: Configure `sampleRate` and `tracesSampleRate` to control event volume (see `sentry-cost-tuning`)
PATCH

echo "Gold patch applied."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-plugins-plus-skills

# Idempotency guard
if grep -qF "Enterprise Sentry architecture patterns for multi-service organizations. Covers " "plugins/saas-packs/sentry-pack/skills/sentry-reference-architecture/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/saas-packs/sentry-pack/skills/sentry-reference-architecture/SKILL.md b/plugins/saas-packs/sentry-pack/skills/sentry-reference-architecture/SKILL.md
@@ -1,294 +1,394 @@
 ---
 name: sentry-reference-architecture
 description: |
-  Design best-practice Sentry architecture for organizations.
-  Use when designing Sentry integration architecture,
-  structuring projects, or planning enterprise rollout.
-  Trigger with phrases like "sentry architecture", "sentry best practices",
-  "design sentry integration", "sentry project structure".
-allowed-tools: Read, Write, Edit, Grep
+  Design production-grade Sentry architecture for multi-service organizations.
+  Use when planning Sentry rollout, structuring projects across teams,
+  building shared config modules, or setting up distributed tracing.
+  Trigger: "sentry architecture", "sentry project structure",
+  "sentry reference design", "sentry distributed tracing".
+allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(npx:*), Glob, Grep
 version: 1.0.0
 license: MIT
 author: Jeremy Longshore <jeremy@intentsolutions.io>
 compatible-with: claude-code, codex, openclaw
-tags: [saas, sentry, architecture, best-practices, enterprise]
-
+tags: [saas, sentry, architecture, enterprise, distributed-tracing, microservices]
 ---
+
 # Sentry Reference Architecture
 
+## Overview
+
+Enterprise Sentry architecture patterns for multi-service organizations. Covers centralized configuration, project topology, team-based alert routing, distributed tracing, error middleware, source map management, and a production-ready SentryService wrapper.
+
 ## Prerequisites
-- Sentry organization created
-- Team structure and service inventory documented
-- Alert escalation paths established
-- Compliance requirements known
+
+- Sentry organization at [sentry.io](https://sentry.io) (Business plan+ for team features)
+- `@sentry/node` v8+ installed (`npm install @sentry/node @sentry/profiling-node`)
+- Service inventory and team ownership documented
+- Node.js 18+ (ESM and native fetch instrumentation)
 
 ## Instructions
 
-### 1. Project Structure Strategy
+### Step 1 — Project Structure Strategy
+
+**Pattern A: One Project Per Service (3+ services, recommended)**
 
-**Pattern A: One Project Per Service (Recommended)**
 ```
 Organization: acme-corp
-├── Team: platform
-│   ├── Project: api-gateway
-│   ├── Project: auth-service
-│   └── Project: user-service
+├── Team: platform-eng
+│   ├── Project: api-gateway       (Node/Express)
+│   ├── Project: auth-service      (Node/Fastify)
+│   └── Project: user-service      (Node/Express)
 ├── Team: payments
-│   ├── Project: payment-api
-│   └── Project: billing-worker
-├── Team: frontend
-│   ├── Project: web-app
-│   └── Project: mobile-app
-└── Team: data
-    ├── Project: etl-pipeline
-    └── Project: analytics-api
+│   ├── Project: payment-api       (Node/Express)
+│   └── Project: billing-worker    (Node worker)
+└── Team: frontend
+    ├── Project: web-app           (React/Next.js)
+    └── Project: mobile-app        (React Native)
 ```
 
-**Benefits:** Clear ownership, independent quotas, team-scoped alerts.
+Benefits: independent quotas, team-scoped alerts, per-service rate limits, isolated release tracking.
 
-**Pattern B: One Project with Environment Tags (Small teams)**
-```
-Organization: startup-xyz
-└── Project: main-app
-    ├── Environment: production
-    ├── Environment: staging
-    └── Environment: development
-```
-
-**Benefits:** Simpler setup, unified issue view across environments.
+**Pattern B: Shared Project (< 3 services, single team)** — one project with `Environment` tags (production/staging/dev). Simpler setup; outgrow when alert noise exceeds one team.
 
-### 2. Shared Configuration Package
+### Step 2 — Centralized Config Module
 
-Create an internal npm package for consistent SDK setup across services:
+Create `lib/sentry.ts` imported by every service to enforce org-wide defaults:
 
 ```typescript
-// packages/sentry-config/index.ts
+// lib/sentry.ts
 import * as Sentry from '@sentry/node';
+import { nodeProfilingIntegration } from '@sentry/profiling-node';
 
-interface ServiceConfig {
+export interface SentryServiceConfig {
   serviceName: string;
   dsn: string;
   environment?: string;
   version?: string;
   tracesSampleRate?: number;
-  additionalIntegrations?: Sentry.Integration[];
+  ignoredTransactions?: string[];
 }
 
-export function initSentry(config: ServiceConfig) {
+export function initSentry(config: SentryServiceConfig): void {
+  const env = config.environment || process.env.NODE_ENV || 'development';
   Sentry.init({
     dsn: config.dsn,
-    environment: config.environment || process.env.NODE_ENV || 'development',
+    environment: env,
     release: `${config.serviceName}@${config.version || 'unknown'}`,
     serverName: config.serviceName,
-
-    // Organization defaults
+    tracesSampleRate: config.tracesSampleRate ?? (env === 'production' ? 0.1 : 1.0),
     sendDefaultPii: false,
-    debug: process.env.NODE_ENV !== 'production',
     maxBreadcrumbs: 50,
-
-    tracesSampleRate: config.tracesSampleRate ?? 0.1,
-
-    integrations: [
-      ...(config.additionalIntegrations || []),
-    ],
-
-    // Organization-wide filtering
+    integrations: [nodeProfilingIntegration()],
     ignoreErrors: [
-      'ResizeObserver loop',
-      'Non-Error promise rejection',
+      'ResizeObserver loop completed with undelivered notifications',
       /Loading chunk \d+ failed/,
+      'AbortError',
     ],
-
-    // Mandatory PII scrubbing
+    tracesSampler: ({ name, parentSampled }) => {
+      if (parentSampled !== undefined) return parentSampled;
+      const ignored = config.ignoredTransactions || [
+        'GET /health', 'GET /healthz', 'GET /ready', 'GET /metrics',
+      ];
+      if (ignored.some(p => name.includes(p))) return 0;
+      return config.tracesSampleRate ?? (env === 'production' ? 0.1 : 1.0);
+    },
     beforeSend(event) {
       if (event.request?.headers) {
-        delete event.request.headers['Authorization'];
-        delete event.request.headers['Cookie'];
-        delete event.request.headers['X-Api-Key'];
+        delete event.request.headers['authorization'];
+        delete event.request.headers['cookie'];
+        delete event.request.headers['x-api-key'];
       }
       return event;
     },
-
-    // Standard tags for all events
     initialScope: {
-      tags: {
-        service: config.serviceName,
-        team: process.env.TEAM_NAME || 'unknown',
-      },
+      tags: { service: config.serviceName, team: process.env.TEAM_NAME || 'unassigned' },
     },
   });
 }
+export { Sentry };
+```
+
+Bootstrap in each service:
 
-// Usage in each service:
-// initSentry({ serviceName: 'auth-service', dsn: process.env.SENTRY_DSN });
+```typescript
+import { initSentry } from '@acme/sentry-config';
+initSentry({ serviceName: 'api-gateway', dsn: process.env.SENTRY_DSN! });
+// Must run BEFORE other imports that need instrumentation
 ```
 
-### 3. Global Error Handler Middleware
+### Step 3 — Error Handling Middleware
+
+**Express:**
 
 ```typescript
-// packages/sentry-config/middleware.ts
+// lib/sentry-middleware.ts
 import * as Sentry from '@sentry/node';
-import { Request, Response, NextFunction } from 'express';
-
-export function sentryRequestMiddleware(serviceName: string) {
-  return (req: Request, res: Response, next: NextFunction) => {
-    Sentry.setTag('route', req.route?.path || req.path);
-    Sentry.setTag('method', req.method);
-
-    if (req.user) {
-      Sentry.setUser({
-        id: req.user.id,
-        // Never set email/ip in production
-      });
-    }
+import type { Request, Response, NextFunction, ErrorRequestHandler } from 'express';
 
+export function sentryRequestHandler() {
+  return (req: Request, _res: Response, next: NextFunction): void => {
+    Sentry.setTag('http.route', req.route?.path || req.path);
+    if (req.user) Sentry.setUser({ id: req.user.id });
     next();
   };
 }
 
-// Domain-specific error classes
-export class AppError extends Error {
-  constructor(
-    message: string,
-    public code: string,
-    public httpStatus: number = 500,
-    public severity: Sentry.SeverityLevel = 'error'
-  ) {
-    super(message);
-    this.name = 'AppError';
-  }
-}
-
-export class ValidationError extends AppError {
-  constructor(message: string, public fields: string[]) {
-    super(message, 'VALIDATION_ERROR', 400, 'warning');
-    this.name = 'ValidationError';
-  }
-}
+export const sentryErrorHandler: ErrorRequestHandler = (err, req, res, _next) => {
+  const status = (err as any).statusCode || 500;
+  Sentry.withScope((scope) => {
+    scope.setLevel(status >= 500 ? 'error' : 'warning');
+    scope.setTag('http.status_code', String(status));
+    scope.setContext('request', { method: req.method, url: req.originalUrl });
+    status >= 500 ? Sentry.captureException(err) : Sentry.captureMessage(err.message, 'warning');
+  });
+  res.status(status).json({ error: status >= 500 ? 'Internal server error' : err.message });
+};
+// Wire: app.use(sentryRequestHandler()) → routes → app.use(sentryErrorHandler)
+```
 
-export class ExternalServiceError extends AppError {
-  constructor(service: string, statusCode: number, message: string) {
-    super(`${service}: ${message}`, 'EXTERNAL_SERVICE_ERROR', 502, 'error');
-    this.name = 'ExternalServiceError';
-  }
-}
+**FastAPI (Python):**
+
+```python
+import sentry_sdk, os
+from sentry_sdk.integrations.fastapi import FastApiIntegration
+
+def init_sentry(service_name: str) -> None:
+    sentry_sdk.init(
+        dsn=os.environ["SENTRY_DSN"],
+        environment=os.getenv("ENV", "development"),
+        release=f"{service_name}@{os.getenv('SERVICE_VERSION', 'unknown')}",
+        traces_sample_rate=0.1,
+        send_default_pii=False,
+        integrations=[FastApiIntegration(transaction_style="endpoint")],
+        before_send=lambda event, hint: _scrub(event),
+    )
+
+def _scrub(event):
+    headers = event.get("request", {}).get("headers", {})
+    for k in ["authorization", "cookie", "x-api-key"]:
+        headers.pop(k, None)
+    return event
 ```
 
-### 4. Distributed Tracing Configuration
+### Step 4 — Distributed Tracing
 
-```typescript
-// All services must propagate trace context
+**HTTP (automatic):** SDK v8 auto-propagates `sentry-trace` + `baggage` headers on fetch/http. All services in the same org link automatically.
 
-// Express service — automatic with SDK v8
-// Just ensure all services use the same org and have tracing enabled
+**Message queues (manual propagation):**
 
-// For non-HTTP communication (message queues, gRPC):
+```typescript
+// lib/sentry-queue.ts
 import * as Sentry from '@sentry/node';
 
-// Producer: attach trace headers to message
-function publishMessage(queue: string, payload: object) {
-  const activeSpan = Sentry.getActiveSpan();
-  const headers: Record<string, string> = {};
-
-  if (activeSpan) {
-    headers['sentry-trace'] = Sentry.spanToTraceHeader(activeSpan);
-    headers['baggage'] = Sentry.spanToBaggageHeader(activeSpan) || '';
-  }
-
-  messageQueue.publish(queue, { payload, headers });
+export function publishWithTrace<T>(queue: string, payload: T, publish: Function) {
+  return Sentry.startSpan({ name: `queue.publish.${queue}`, op: 'queue.publish' }, async () => {
+    const headers: Record<string, string> = {};
+    const span = Sentry.getActiveSpan();
+    if (span) {
+      headers['sentry-trace'] = Sentry.spanToTraceHeader(span);
+      headers['baggage'] = Sentry.spanToBaggageHeader(span) || '';
+    }
+    await publish(queue, { payload, headers });
+  });
 }
 
-// Consumer: continue trace from message headers
-function onMessage(msg: { payload: object; headers: Record<string, string> }) {
-  Sentry.continueTrace(
-    {
-      sentryTrace: msg.headers['sentry-trace'],
-      baggage: msg.headers['baggage'],
-    },
-    () => {
-      Sentry.startSpan(
-        { name: `queue.process.${msg.payload.type}`, op: 'queue.task' },
-        () => processMessage(msg.payload)
-      );
-    }
+export function consumeWithTrace<T>(queue: string, msg: { payload: T; headers: Record<string, string> }, handler: (p: T) => Promise<void>) {
+  return Sentry.continueTrace(
+    { sentryTrace: msg.headers['sentry-trace'], baggage: msg.headers['baggage'] },
+    () => Sentry.startSpan({ name: `queue.process.${queue}`, op: 'queue.process' }, () => handler(msg.payload))
   );
 }
 ```
 
-### 5. Alert Hierarchy
+### Step 5 — Team-Based Alert Routing
 
-```
-Tier 1 — Critical (P0)
-  Trigger: Error rate > 50/min OR crash-free sessions < 95%
-  Action: PagerDuty → on-call engineer
-  Response: 15 min acknowledge, 1 hour resolve
-
-Tier 2 — Warning (P1)
-  Trigger: New issue in production OR regression detected
-  Action: Slack #alerts-production
-  Response: Same business day
-
-Tier 3 — Info (P2)
-  Trigger: P95 latency > 2s OR error rate > 10/min
-  Action: Slack #alerts-performance
-  Response: Next sprint
-
-Tier 4 — Low (P3)
-  Trigger: New issue in staging
-  Action: Slack #alerts-staging
-  Response: Backlog triage
+Configure in **Project Settings > Ownership Rules**:
+
+```bash
+# .sentry/ownership-rules
+path:src/payments/**     #payments-team
+path:src/auth/**         #platform-team
+url:*/api/v1/payments/*  #payments-team
+tags.service:payment-api #payments-team
+*                        #platform-team
 ```
 
-### 6. Issue Routing by Team
+**Alert tiers:**
+- **P0 Critical:** error rate > 50/min OR crash-free < 95% — PagerDuty on-call, 15 min SLA
+- **P1 Warning:** new production issue or regression — Slack #alerts-prod, same-day SLA
+- **P2 Performance:** P95 > 2s or Apdex < 0.7 — Slack #alerts-perf, next sprint
+- **P3 Info:** new staging issue — Slack #alerts-staging, backlog triage
+
+### Step 6 — Source Map Uploads (Monorepo)
+
+```bash
+#!/usr/bin/env bash
+# scripts/upload-sourcemaps.sh — run in CI after build
+set -euo pipefail
+SERVICE="${1:?Usage: upload-sourcemaps.sh <service>}"
+RELEASE="${SERVICE}@$(git rev-parse --short HEAD)"
+
+npx @sentry/cli releases new "$RELEASE" --org "$SENTRY_ORG" --project "$SERVICE"
+npx @sentry/cli sourcemaps upload --org "$SENTRY_ORG" --project "$SERVICE" \
+  --release "$RELEASE" --url-prefix "~/" --validate "./services/${SERVICE}/dist/"
+npx @sentry/cli releases set-commits "$RELEASE" --org "$SENTRY_ORG" --auto
+npx @sentry/cli releases finalize "$RELEASE" --org "$SENTRY_ORG"
+```
 
-Configure ownership rules in **Project Settings > Ownership Rules**:
+Webpack plugin alternative (auto-uploads on build):
 
+```typescript
+import { sentryWebpackPlugin } from '@sentry/webpack-plugin';
+export default {
+  devtool: 'source-map',
+  plugins: [sentryWebpackPlugin({
+    org: process.env.SENTRY_ORG,
+    project: 'web-app',
+    authToken: process.env.SENTRY_AUTH_TOKEN,
+    sourcemaps: { filesToDeleteAfterUpload: ['./dist/**/*.map'] },
+  })],
+};
 ```
-# Route by file path
-path:src/payments/* #payments-team
-path:src/auth/* #platform-team
-path:src/api/* #backend-team
 
-# Route by URL
-url:*/api/v1/payments/* #payments-team
-url:*/api/v1/users/* #platform-team
+### Step 7 — Custom Integrations
 
-# Route by tag
-tags.service:payment-api #payments-team
-tags.service:auth-service #platform-team
+Wrap internal SDK calls with spans for tracing visibility:
+
+```typescript
+import * as Sentry from '@sentry/node';
+export function withSpan<T>(op: string, desc: string, fn: () => Promise<T>, attrs?: Record<string, string | number>): Promise<T> {
+  return Sentry.startSpan({ name: desc, op, attributes: attrs }, async (span) => {
+    try { const r = await fn(); span.setStatus({ code: 1, message: 'ok' }); return r; }
+    catch (e) { span.setStatus({ code: 2, message: String(e) }); throw e; }
+  });
+}
+// Usage: await withSpan('payment.charge', 'charge $50', () => gateway.charge(5000, 'usd', custId));
 ```
 
-### 7. Release Strategy
+### Step 8 — SentryService Wrapper
+
+Production wrapper with singleton, metrics, and graceful shutdown:
+
+```typescript
+// lib/sentry-service.ts
+import * as Sentry from '@sentry/node';
+
+export class SentryService {
+  private static instance: SentryService | null = null;
+  private initialized = false;
+
+  private constructor(private config: { serviceName: string; dsn: string; version?: string }) {}
+
+  static getInstance(config?: { serviceName: string; dsn: string; version?: string }): SentryService {
+    if (!SentryService.instance) {
+      if (!config) throw new Error('Config required on first call');
+      SentryService.instance = new SentryService(config);
+    }
+    return SentryService.instance;
+  }
 
+  init(): void {
+    if (this.initialized) return;
+    const { initSentry } = require('./sentry');
+    initSentry(this.config);
+    this.initialized = true;
+  }
+
+  captureError(error: Error, ctx?: { tags?: Record<string, string>; extra?: Record<string, unknown>; level?: Sentry.SeverityLevel }): string {
+    return Sentry.withScope((scope) => {
+      if (ctx?.tags) Object.entries(ctx.tags).forEach(([k, v]) => scope.setTag(k, v));
+      if (ctx?.extra) Object.entries(ctx.extra).forEach(([k, v]) => scope.setExtra(k, v));
+      if (ctx?.level) scope.setLevel(ctx.level);
+      return Sentry.captureException(error);
+    });
+  }
+
+  async trackOperation<T>(name: string, op: string, fn: () => Promise<T>): Promise<T> {
+    return Sentry.startSpan({ name, op }, async (span) => {
+      try { const r = await fn(); span.setStatus({ code: 1, message: 'ok' }); return r; }
+      catch (e) { span.setStatus({ code: 2, message: String(e) }); Sentry.captureException(e); throw e; }
+    });
+  }
+
+  async shutdown(timeoutMs = 5000): Promise<void> {
+    await Sentry.close(timeoutMs);
+    SentryService.instance = null;
+    this.initialized = false;
+  }
+}
 ```
-Release naming: {service}@{semver}+{git-sha-short}
-Examples:
-  api-gateway@2.1.0+abc1234
-  web-app@3.5.2+def5678
-  payment-api@1.8.0+ghi9012
-
-Each service creates its own release in its own project.
-Distributed traces link events across services automatically.
+
+### Step 9 — Health Check Exclusion
+
+Define health routes BEFORE Sentry middleware so they never create transactions:
+
+```typescript
+app.get('/health', (_req, res) => res.status(200).json({ status: 'ok' }));
+app.get('/readiness', async (_req, res) => {
+  const dbOk = await checkDatabase();
+  res.status(dbOk ? 200 : 503).json({ db: dbOk });
+});
+// Combined with tracesSampler (Step 2) dropping /health, /ready, /metrics
 ```
 
 ## Output
-- Project structure following one-project-per-service pattern
-- Shared configuration package enforcing organization defaults
-- Domain-specific error classes with consistent tagging
-- Distributed tracing configured across all services
-- Alert hierarchy with team routing and escalation paths
+
+- Centralized `lib/sentry.ts` enforcing PII scrubbing, sample rates, and noise filters across all services
+- Project-per-service topology with team ownership, independent quotas, and per-service releases
+- Error middleware for Express and FastAPI with severity-based capture
+- Distributed tracing across HTTP (automatic) and message queues (manual propagation helpers)
+- Team-based alert routing with 4-tier escalation (P0-P3)
+- Source map pipeline with CLI and Webpack plugin for monorepo builds
+- SentryService singleton with custom metrics and graceful shutdown
 
 ## Error Handling
 
 | Error | Cause | Solution |
 |-------|-------|----------|
-| Cross-service traces not linking | Missing trace header propagation | Ensure `sentry-trace` and `baggage` headers forwarded |
-| Alerts going to wrong team | Ownership rules not configured | Set up ownership rules in project settings |
-| Inconsistent SDK config across services | No shared config package | Create and enforce shared configuration package |
-| Alert fatigue | Too many low-priority alerts | Implement tiered alert hierarchy with appropriate thresholds |
+| Traces not linking cross-service | Missing trace headers in non-HTTP transport | Use `publishWithTrace`/`consumeWithTrace` for queues |
+| `init() called multiple times` | Multiple imports | Use SentryService singleton (idempotent init) |
+| Source maps not resolving | Wrong `url-prefix` | Use `--url-prefix "~/"` and `--validate` flag |
+| Alerts routing to wrong team | Ownership rules mismatch | Verify `path:` rules match source tree; add `tags.service:` fallback |
+| Health checks consuming quota | Probes hitting instrumented routes | Define health routes before middleware; use `tracesSampler` |
+| PII leaking | Missing `beforeSend` scrubbing | Enforce `sendDefaultPii: false` + header deletion in shared config |
+
+## Examples
+
+**Bootstrap a service (3 lines):**
+```typescript
+import { SentryService } from '@acme/sentry-config';
+const sentry = SentryService.getInstance({ serviceName: 'user-service', dsn: process.env.SENTRY_DSN! });
+sentry.init();
+```
+
+**Capture with business context:**
+```typescript
+sentry.captureError(err, {
+  tags: { 'payment.provider': 'stripe' },
+  extra: { orderId: order.id, amount: order.total },
+  level: 'error',
+});
+```
+
+**Track an operation:**
+```typescript
+const result = await sentry.trackOperation('order.fulfillment', 'business.process', () => fulfillOrder(id));
+```
 
 ## Resources
-- [Best Practices](https://docs.sentry.io/product/issues/best-practices/)
+
+- [Sentry Node.js SDK v8](https://docs.sentry.io/platforms/javascript/guides/node/)
 - [Distributed Tracing](https://docs.sentry.io/product/performance/distributed-tracing/)
 - [Ownership Rules](https://docs.sentry.io/product/issues/ownership-rules/)
+- [Source Maps CLI](https://docs.sentry.io/platforms/javascript/sourcemaps/uploading/cli/)
 - [Alerting Best Practices](https://docs.sentry.io/product/alerts/best-practices/)
+- [Sentry Webpack Plugin](https://www.npmjs.com/package/@sentry/webpack-plugin)
+
+## Next Steps
+
+1. Roll out incrementally — start with one high-traffic service, validate traces and alerts, then onboard remaining services
+2. Set up Sentry Crons for scheduled job monitoring (ETL, billing workers)
+3. Enable Session Replay (`@sentry/browser`) for frontend error-to-session correlation
+4. Define per-project quota budgets to prevent one noisy service from exhausting org quota
+5. Build Discover dashboards for cross-service error trends (`count() by service, level`)
PATCH

echo "Gold patch applied."

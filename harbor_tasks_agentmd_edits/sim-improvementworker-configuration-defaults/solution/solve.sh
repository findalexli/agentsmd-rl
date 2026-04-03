#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sim

# Idempotent: skip if already applied
if grep -q 'worker/index.js' docker-compose.local.yml 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/README.md b/README.md
index 831361fb3ed..114d5ffc207 100644
--- a/README.md
+++ b/README.md
@@ -74,6 +74,10 @@ docker compose -f docker-compose.prod.yml up -d

 Open [http://localhost:3000](http://localhost:3000)

+#### Background worker note
+
+The Docker Compose stack starts a dedicated worker container by default. If `REDIS_URL` is not configured, the worker will start, log that it is idle, and do no queue processing. This is expected. Queue-backed API, webhook, and schedule execution requires Redis; installs without Redis continue to use the inline execution path.
+
 Sim also supports local models via [Ollama](https://ollama.ai) and [vLLM](https://docs.vllm.ai/) — see the [Docker self-hosting docs](https://docs.sim.ai/self-hosting/docker) for setup details.

 ### Self-hosted: Manual Setup
@@ -113,10 +117,12 @@ cd packages/db && bunx drizzle-kit migrate --config=./drizzle.config.ts
 5. Start development servers:

 ```bash
-bun run dev:full  # Starts both Next.js app and realtime socket server
+bun run dev:full  # Starts Next.js app, realtime socket server, and the BullMQ worker
 ```

-Or run separately: `bun run dev` (Next.js) and `cd apps/sim && bun run dev:sockets` (realtime).
+If `REDIS_URL` is not configured, the worker will remain idle and execution continues inline.
+
+Or run separately: `bun run dev` (Next.js), `cd apps/sim && bun run dev:sockets` (realtime), and `cd apps/sim && bun run worker` (BullMQ worker).

 ## Copilot API Keys

diff --git a/apps/sim/lib/execution/isolated-vm.ts b/apps/sim/lib/execution/isolated-vm.ts
index 9deffbe83c0..877035760e5 100644
--- a/apps/sim/lib/execution/isolated-vm.ts
+++ b/apps/sim/lib/execution/isolated-vm.ts
@@ -696,6 +696,8 @@ function spawnWorker(): Promise<WorkerInfo> {
     const currentDir = path.dirname(fileURLToPath(import.meta.url))
     const candidatePaths = [
       path.join(currentDir, 'isolated-vm-worker.cjs'),
+      path.join(currentDir, '..', '..', 'lib', 'execution', 'isolated-vm-worker.cjs'),
+      path.join(process.cwd(), 'apps', 'sim', 'lib', 'execution', 'isolated-vm-worker.cjs'),
       path.join(process.cwd(), 'lib', 'execution', 'isolated-vm-worker.cjs'),
     ]
     const workerPath = candidatePaths.find((p) => fs.existsSync(p))
diff --git a/apps/sim/package.json b/apps/sim/package.json
index c8cc4530338..6a882cb447b 100644
--- a/apps/sim/package.json
+++ b/apps/sim/package.json
@@ -18,7 +18,7 @@
     "load:workflow:isolation": "BASE_URL=${BASE_URL:-http://localhost:3000} ISOLATION_DURATION=${ISOLATION_DURATION:-30} TOTAL_RATE=${TOTAL_RATE:-9} WORKSPACE_A_WEIGHT=${WORKSPACE_A_WEIGHT:-8} WORKSPACE_B_WEIGHT=${WORKSPACE_B_WEIGHT:-1} bunx artillery run scripts/load/workflow-isolation.yml",
     "build": "bun run build:pptx-worker && bun run build:worker && next build",
     "build:pptx-worker": "bun build ./lib/execution/pptx-worker.cjs --target=node --format=cjs --outfile ./dist/pptx-worker.cjs",
-    "build:worker": "bun build ./worker/index.ts --target=node --format=cjs --packages=external --outfile ./dist/worker.cjs",
+    "build:worker": "bun build ./worker/index.ts --target=node --format=esm --splitting --outdir ./dist/worker --external isolated-vm",
     "start": "next start",
     "worker": "NODE_ENV=production bun run worker/index.ts",
     "prepare": "cd ../.. && bun husky",
diff --git a/docker-compose.local.yml b/docker-compose.local.yml
index ceb8dc3883b..354a77d1393 100644
--- a/docker-compose.local.yml
+++ b/docker-compose.local.yml
@@ -32,7 +32,7 @@ services:
       realtime:
         condition: service_healthy
     healthcheck:
-      test: ['CMD', 'wget', '--spider', '--quiet', 'http://127.0.0.1:3000']
+      test: ['CMD', 'curl', '-fsS', 'http://127.0.0.1:3000']
       interval: 90s
       timeout: 5s
       retries: 3
@@ -61,7 +61,7 @@ services:
         limits:
           memory: 1G
     healthcheck:
-      test: ['CMD', 'wget', '--spider', '--quiet', 'http://127.0.0.1:3002/health']
+      test: ['CMD', 'curl', '-fsS', 'http://127.0.0.1:3002/health']
       interval: 90s
       timeout: 5s
       retries: 3
@@ -71,10 +71,8 @@ services:
     build:
       context: .
       dockerfile: docker/app.Dockerfile
-    command: ['bun', 'apps/sim/dist/worker.cjs']
+    command: ['bun', 'apps/sim/dist/worker/index.js']
     restart: unless-stopped
-    profiles:
-      - worker
     deploy:
       resources:
         limits:
@@ -93,7 +91,7 @@ services:
       migrations:
         condition: service_completed_successfully
     healthcheck:
-      test: ['CMD', 'wget', '--spider', '--quiet', 'http://127.0.0.1:3001/health/live']
+      test: ['CMD', 'curl', '-fsS', 'http://127.0.0.1:3001/health/live']
       interval: 90s
       timeout: 5s
       retries: 3
diff --git a/docker-compose.prod.yml b/docker-compose.prod.yml
index da547506556..5f8f8bc9db5 100644
--- a/docker-compose.prod.yml
+++ b/docker-compose.prod.yml
@@ -34,7 +34,7 @@ services:
       realtime:
         condition: service_healthy
     healthcheck:
-      test: ['CMD', 'wget', '--spider', '--quiet', 'http://127.0.0.1:3000']
+      test: ['CMD', 'curl', '-fsS', 'http://127.0.0.1:3000']
       interval: 90s
       timeout: 5s
       retries: 3
@@ -42,7 +42,7 @@ services:

   sim-worker:
     image: ghcr.io/simstudioai/simstudio:latest
-    command: ['bun', 'apps/sim/dist/worker.cjs']
+    command: ['bun', 'apps/sim/dist/worker/index.js']
     restart: unless-stopped
     deploy:
       resources:
@@ -71,7 +71,7 @@ services:
       migrations:
         condition: service_completed_successfully
     healthcheck:
-      test: ['CMD', 'wget', '--spider', '--quiet', 'http://127.0.0.1:${WORKER_PORT:-3001}/health/live']
+      test: ['CMD', 'curl', '-fsS', 'http://127.0.0.1:${WORKER_PORT:-3001}/health/live']
       interval: 90s
       timeout: 5s
       retries: 3
@@ -98,7 +98,7 @@ services:
       db:
         condition: service_healthy
     healthcheck:
-      test: ['CMD', 'wget', '--spider', '--quiet', 'http://127.0.0.1:3002/health']
+      test: ['CMD', 'curl', '-fsS', 'http://127.0.0.1:3002/health']
       interval: 90s
       timeout: 5s
       retries: 3
diff --git a/docker/app.Dockerfile b/docker/app.Dockerfile
index b5f7970b9d8..b5e2f14457b 100644
--- a/docker/app.Dockerfile
+++ b/docker/app.Dockerfile
@@ -114,12 +114,8 @@ COPY --from=builder --chown=nextjs:nodejs /app/apps/sim/lib/execution/isolated-v
 # Copy the bundled PPTX worker artifact
 COPY --from=builder --chown=nextjs:nodejs /app/apps/sim/dist/pptx-worker.cjs ./apps/sim/dist/pptx-worker.cjs

-# Copy the bundled BullMQ worker artifact and workspace packages it needs at runtime.
-# The bundle uses --packages=external so all node_modules are resolved at runtime.
-# npm packages come from the standalone node_modules; workspace packages need explicit copies.
-COPY --from=builder --chown=nextjs:nodejs /app/apps/sim/dist/worker.cjs ./apps/sim/dist/worker.cjs
-COPY --from=builder --chown=nextjs:nodejs /app/packages/logger ./node_modules/@sim/logger
-COPY --from=builder --chown=nextjs:nodejs /app/packages/db ./node_modules/@sim/db
+# Copy the bundled BullMQ worker (self-contained ESM bundle, only isolated-vm is external)
+COPY --from=builder --chown=nextjs:nodejs /app/apps/sim/dist/worker ./apps/sim/dist/worker

 # Guardrails setup with pip caching
 COPY --from=builder --chown=nextjs:nodejs /app/apps/sim/lib/guardrails/requirements.txt ./apps/sim/lib/guardrails/requirements.txt
diff --git a/docker/realtime.Dockerfile b/docker/realtime.Dockerfile
index 337e5e2afdb..add2c194a99 100644
--- a/docker/realtime.Dockerfile
+++ b/docker/realtime.Dockerfile
@@ -3,11 +3,12 @@
 # ========================================
 FROM oven/bun:1.3.11-alpine AS base

+RUN apk add --no-cache libc6-compat curl
+
 # ========================================
 # Dependencies Stage: Install Dependencies
 # ========================================
 FROM base AS deps
-RUN apk add --no-cache libc6-compat
 WORKDIR /app

 COPY package.json bun.lock turbo.json ./
diff --git a/helm/sim/README.md b/helm/sim/README.md
index 0c33120539b..3507f543495 100644
--- a/helm/sim/README.md
+++ b/helm/sim/README.md
@@ -709,6 +709,17 @@ kubectl create secret generic my-postgresql-secret \

 See `examples/values-existing-secret.yaml` for more details.

+### Worker and Redis
+
+The Helm chart enables the BullMQ worker by default so the deployment topology matches Docker Compose. If `REDIS_URL` is not configured, the worker pod will still start but remain idle and do no queue processing. This is expected.
+
+Queue-backed API, webhook, and schedule execution requires Redis. Installs without Redis continue to use the inline execution path. If you do not want the worker pod at all, set:
+
+```yaml
+worker:
+  enabled: false
+```
+
 ### External Secrets Parameters

 | Parameter | Description | Default |
diff --git a/helm/sim/templates/_helpers.tpl b/helm/sim/templates/_helpers.tpl
index 3ba078c5e67..915df7cf618 100644
--- a/helm/sim/templates/_helpers.tpl
+++ b/helm/sim/templates/_helpers.tpl
@@ -222,10 +222,6 @@ Skip validation when using existing secrets or External Secrets Operator
 {{- fail "realtime.env.BETTER_AUTH_SECRET must not use the default placeholder value. Generate a secure secret with: openssl rand -hex 32" }}
 {{- end }}
 {{- end }}
-{{- /* Worker validation - REDIS_URL is required when worker is enabled */ -}}
-{{- if and .Values.worker.enabled (not .Values.app.env.REDIS_URL) }}
-{{- fail "app.env.REDIS_URL is required when worker.enabled=true" }}
-{{- end }}
 {{- /* PostgreSQL password validation - skip if using existing secret or ESO */ -}}
 {{- if not (or $useExistingPostgresSecret $useExternalSecrets) }}
 {{- if and .Values.postgresql.enabled (not .Values.postgresql.auth.password) }}
diff --git a/helm/sim/templates/deployment-worker.yaml b/helm/sim/templates/deployment-worker.yaml
index 701fdff1849..adf7b9c284f 100644
--- a/helm/sim/templates/deployment-worker.yaml
+++ b/helm/sim/templates/deployment-worker.yaml
@@ -37,7 +37,7 @@ spec:
         - name: worker
           image: {{ include "sim.image" (dict "context" . "image" .Values.worker.image) }}
           imagePullPolicy: {{ .Values.worker.image.pullPolicy }}
-          command: ["bun", "apps/sim/dist/worker.cjs"]
+          command: ["bun", "apps/sim/dist/worker/index.js"]
           ports:
             - name: health
               containerPort: {{ .Values.worker.healthPort }}
diff --git a/helm/sim/templates/external-secret-app.yaml b/helm/sim/templates/external-secret-app.yaml
index 3377901fcc3..b5b2b8fa34b 100644
--- a/helm/sim/templates/external-secret-app.yaml
+++ b/helm/sim/templates/external-secret-app.yaml
@@ -41,4 +41,9 @@ spec:
       remoteRef:
         key: {{ .Values.externalSecrets.remoteRefs.app.API_ENCRYPTION_KEY }}
     {{- end }}
+    {{- if .Values.externalSecrets.remoteRefs.app.REDIS_URL }}
+    - secretKey: REDIS_URL
+      remoteRef:
+        key: {{ .Values.externalSecrets.remoteRefs.app.REDIS_URL }}
+    {{- end }}
 {{- end }}
diff --git a/helm/sim/templates/secrets-app.yaml b/helm/sim/templates/secrets-app.yaml
index 29a9d065f2d..c99e485384b 100644
--- a/helm/sim/templates/secrets-app.yaml
+++ b/helm/sim/templates/secrets-app.yaml
@@ -24,4 +24,7 @@ stringData:
   {{- if .Values.app.env.API_ENCRYPTION_KEY }}
   API_ENCRYPTION_KEY: {{ .Values.app.env.API_ENCRYPTION_KEY | quote }}
   {{- end }}
+  {{- if .Values.app.env.REDIS_URL }}
+  REDIS_URL: {{ .Values.app.env.REDIS_URL | quote }}
+  {{- end }}
 {{- end }}
diff --git a/helm/sim/values.yaml b/helm/sim/values.yaml
index 4fd2828d8c0..92c163b4222 100644
--- a/helm/sim/values.yaml
+++ b/helm/sim/values.yaml
@@ -64,6 +64,7 @@ app:
         INTERNAL_API_SECRET: "INTERNAL_API_SECRET"
         CRON_SECRET: "CRON_SECRET"
         API_ENCRYPTION_KEY: "API_ENCRYPTION_KEY"
+        REDIS_URL: "REDIS_URL"

   # Environment variables
   env:
@@ -95,6 +96,7 @@ app:
     # Optional: API Key Encryption (RECOMMENDED for production)
     # Generate 64-character hex string using: openssl rand -hex 32 (outputs 64 hex chars = 32 bytes)
     API_ENCRYPTION_KEY: ""  # OPTIONAL - encrypts API keys at rest, must be exactly 64 hex characters, if not set keys stored in plain text
+    REDIS_URL: ""           # OPTIONAL - Redis connection string for BullMQ/workers; can also come from app secret or External Secrets

     # Email & Communication
     EMAIL_VERIFICATION_ENABLED: "false"                   # Enable email verification for user registration and login (defaults to false)
@@ -359,10 +361,12 @@ realtime:
   extraVolumeMounts: []

 # BullMQ worker configuration (processes background jobs when Redis is available)
-# Uses the same image as the main app with a different command
+# Uses the same image as the main app with a different command.
+# Enabled by default so self-hosted deployments get the same topology as compose.
+# Without REDIS_URL the worker starts, logs that it is idle, and does no queue processing.
 worker:
-  # Enable/disable the worker deployment (requires REDIS_URL to be set in app.env)
-  enabled: false
+  # Enable/disable the worker deployment
+  enabled: true

   # Image configuration (defaults to same image as app)
   image:
@@ -1283,6 +1287,8 @@ externalSecrets:
       CRON_SECRET: ""
       # Path to API_ENCRYPTION_KEY in external store (optional)
       API_ENCRYPTION_KEY: ""
+      # Path to REDIS_URL in external store (optional, required for worker when not set in app.env)
+      REDIS_URL: ""

     # PostgreSQL password (for internal PostgreSQL)
     postgresql:

PATCH

echo "Patch applied successfully."

#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Check if already applied
if grep -q "RUN mkdir .next" examples/with-docker/Dockerfile 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/examples/with-docker/Dockerfile b/examples/with-docker/Dockerfile
index 420ce8ecfaa88e..607a92a5a3b0c3 100644
--- a/examples/with-docker/Dockerfile
+++ b/examples/with-docker/Dockerfile
@@ -52,8 +52,12 @@ ENV NODE_ENV=production
 # ENV NEXT_TELEMETRY_DISABLED=1

 # Build Next.js application
-RUN --mount=type=cache,target=/app/.next/cache \
-  if [ -f package-lock.json ]; then \
+# If you want to speed up Docker rebuilds, you can cache the build artifacts
+# by adding: --mount=type=cache,target=/app/.next/cache
+# This caches the .next/cache directory across builds, but it also prevents
+# .next/cache/fetch-cache from being included in the final image, meaning
+# cached fetch responses from the build won't be available at runtime.
+RUN if [ -f package-lock.json ]; then \
     npm run build; \
   elif [ -f yarn.lock ]; then \
     corepack enable yarn && yarn build; \
@@ -84,9 +88,20 @@ ENV HOSTNAME="0.0.0.0"

 # Copy production assets
 COPY --from=builder --chown=node:node /app/public ./public
+
+# Set the correct permission for prerender cache
+RUN mkdir .next
+RUN chown node:node .next
+
+# Automatically leverage output traces to reduce image size
+# https://nextjs.org/docs/advanced-features/output-file-tracing
 COPY --from=builder --chown=node:node /app/.next/standalone ./
 COPY --from=builder --chown=node:node /app/.next/static ./.next/static

+# If you want to persist the fetch cache generated during the build so that
+# cached responses are available immediately on startup, uncomment this line:
+# COPY --from=builder --chown=node:node /app/.next/cache ./.next/cache
+
 # Switch to non-root user for security best practices
 USER node

diff --git a/examples/with-docker/Dockerfile.bun b/examples/with-docker/Dockerfile.bun
index 7c0d14674b6341..35de9f3fab2e1d 100644
--- a/examples/with-docker/Dockerfile.bun
+++ b/examples/with-docker/Dockerfile.bun
@@ -63,9 +63,20 @@ ENV HOSTNAME="0.0.0.0"

 # Copy production assets
 COPY --from=builder --chown=bun:bun /app/public ./public
+
+# Set the correct permission for prerender cache
+RUN mkdir .next
+RUN chown bun:bun .next
+
+# Automatically leverage output traces to reduce image size
+# https://nextjs.org/docs/advanced-features/output-file-tracing
 COPY --from=builder --chown=bun:bun /app/.next/standalone ./
 COPY --from=builder --chown=bun:bun /app/.next/static ./.next/static

+# If you want to persist the fetch cache generated during the build so that
+# cached responses are available immediately on startup, uncomment this line:
+# COPY --from=builder --chown=bun:bun /app/.next/cache ./.next/cache
+
 # Switch to non-root user for security best practices
 USER bun

diff --git a/examples/with-docker/README.md b/examples/with-docker/README.md
index cca3ecaff158db..7db8a64ccaf67d 100644
--- a/examples/with-docker/README.md
+++ b/examples/with-docker/README.md
@@ -4,12 +4,12 @@ A production-ready example demonstrating how to Dockerize Next.js applications u

 ## Features

-- ✅ Multi-stage Docker build for optimal image size
-- ✅ Next.js standalone mode for minimal production builds
-- ✅ Security best practices (non-root user)
-- ✅ Slim Linux base image for optimal compatibility and smaller size
-- ✅ BuildKit cache mounts for faster builds
-- ✅ Production-ready configuration
+- Multi-stage Docker build for optimal image size
+- Next.js standalone mode for minimal production builds
+- Security best practices (non-root user)
+- Slim Linux base image for optimal compatibility and smaller size
+- BuildKit cache mounts for faster builds
+- Production-ready configuration

 ## Prerequisites

@@ -127,10 +127,11 @@ Learn more about [Next.js standalone output](https://nextjs.org/docs/pages/api-r

 - **Multi-stage build**: Separates dependency installation (`dependencies`), build (`builder`), and runtime (`runner`) stages
 - **Slim Linux**: Uses `slim` image tag for optimal compatibility and smaller image size
-- **BuildKit cache mounts**: Speeds up builds by caching package manager stores (`/root/.npm`, `/usr/local/share/.cache/yarn`, `/root/.local/share/pnpm/store`) and Next.js build cache (`/app/.next/cache`)
+- **BuildKit cache mounts**: Speeds up builds by caching package manager stores (`/root/.npm`, `/usr/local/share/.cache/yarn`, `/root/.local/share/pnpm/store`). See the Dockerfile for an optional `.next/cache` mount to speed up rebuilds.
 - **Non-root user**: Runs as `node` user for security
 - **Optimized layers**: Leverages Docker layer caching effectively
 - **Standalone output**: Copies only the necessary files from `.next/standalone` and `.next/static`
+- **Writable `.next` directory**: The `.next` directory is created and owned by the `node` user so the server can write prerender cache and optimized images at runtime
 - **Node.js version maintenance**: Uses Node.js 24.13.0-slim (latest LTS at time of writing). Update the `NODE_VERSION` ARG to the latest LTS version for security updates.

 ### Dockerfile.bun Highlights (Bun)
@@ -139,7 +140,7 @@ Learn more about [Next.js standalone output](https://nextjs.org/docs/pages/api-r
 - **Official Bun image**: Uses `oven/bun:1` for optimal Bun performance
 - **Non-root user**: Runs as built-in `bun` user for security
 - **Frozen lockfile**: Uses `bun.lock` for reproducible builds
-- **Standalone output**: Same optimized output as the Node.js version
+- **Standalone output**: Same optimized output as the Node.js version, with writable `.next` directory for runtime cache

 **Why Node.js slim image tag?**: The slim variant provides optimal compatibility with npm packages and native dependencies while maintaining a smaller image size (~226MB). Slim uses glibc (standard Linux), ensuring better compatibility than Alpine's musl libc, which can cause issues with some npm packages. This makes it ideal for public examples where reliability and compatibility are priorities.

@@ -152,7 +153,8 @@ Learn more about [Next.js standalone output](https://nextjs.org/docs/pages/api-r

 To switch to Alpine, simply change the `NODE_VERSION` ARG in the Dockerfile to `24.11.1-alpine`.

-**⚠️ Important - Node.js Version Maintenance**: This Dockerfile uses Node.js 24.13.0-slim, which was the latest LTS version at the time of writing. To ensure security and stay up-to-date, regularly check and update the `NODE_VERSION` ARG in the Dockerfile to the latest Node.js LTS version. Check the latest version at [Nodejs official website](https://nodejs.org/) and browse available Node.js images on [Docker Hub](https://hub.docker.com/_/node).
+> [!IMPORTANT]
+> **Node.js Version Maintenance**: This Dockerfile uses Node.js 24.13.0-slim, which was the latest LTS version at the time of writing. To ensure security and stay up-to-date, regularly check and update the `NODE_VERSION` ARG in the Dockerfile to the latest Node.js LTS version. Check the latest version at [Nodejs official website](https://nodejs.org/) and browse available Node.js images on [Docker Hub](https://hub.docker.com/_/node).

 ## Deployment

@@ -175,9 +177,11 @@ This example can be deployed to any container-based platform:
    ```
    This will also enable Cloud Build for your project.
 5. Deploy to Cloud Run:
+
    ```bash
    gcloud run deploy --image gcr.io/PROJECT-ID/nextjs-docker --project PROJECT-ID --platform managed --allow-unauthenticated
    ```
+
    - You will be prompted for the service name: press Enter to accept the default name, `nextjs-docker`.
    - You will be prompted for [region](https://cloud.google.com/run/docs/quickstarts/build-and-deploy#follow-cloud-run): select the region of your choice, for example `us-central1`.

PATCH

echo "Patch applied successfully."

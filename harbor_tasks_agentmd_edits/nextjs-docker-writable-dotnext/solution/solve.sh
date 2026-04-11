#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q "Set the correct permission for prerender cache" examples/with-docker/Dockerfile 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYTHON'
import re

# Fix with-docker README.md
with open("examples/with-docker/README.md", "r") as f:
    content = f.read()

# Remove checkmark bullets
content = content.replace("- ✅ Multi-stage Docker build for optimal image size", "- Multi-stage Docker build for optimal image size")
content = content.replace("- ✅ Next.js standalone mode for minimal production builds", "- Next.js standalone mode for minimal production builds")
content = content.replace("- ✅ Security best practices (non-root user)", "- Security best practices (non-root user)")
content = content.replace("- ✅ Slim Linux base image for optimal compatibility and smaller size", "- Slim Linux base image for optimal compatibility and smaller size")
content = content.replace("- ✅ BuildKit cache mounts for faster builds", "- BuildKit cache mounts for faster builds")
content = content.replace("- ✅ Production-ready configuration", "- Production-ready configuration")

# Update BuildKit cache mounts line
content = content.replace(
    "- **BuildKit cache mounts**: Speeds up builds by caching package manager stores (`/root/.npm`, `/usr/local/share/.cache/yarn`, `/root/.local/share/pnpm/store`) and Next.js build cache (`/app/.next/cache`)",
    "- **BuildKit cache mounts**: Speeds up builds by caching package manager stores (`/root/.npm`, `/usr/local/share/.cache/yarn`, `/root/.local/share/pnpm/store`). See the Dockerfile for an optional `.next/cache` mount to speed up rebuilds."
)

# Add writable .next directory bullet
content = content.replace(
    "- **Standalone output**: Copies only the necessary files from `.next/standalone` and `.next/static`",
    "- **Standalone output**: Copies only the necessary files from `.next/standalone` and `.next/static`\n- **Writable `.next` directory**: The `.next` directory is created and owned by the `node` user so the server can write prerender cache and optimized images at runtime"
)

# Update standalone output line in bun section
content = content.replace(
    "- **Standalone output**: Same optimized output as the Node.js version",
    "- **Standalone output**: Same optimized output as the Node.js version, with writable `.next` directory for runtime cache"
)

# Convert Important section to GitHub callout
old_important = """**⚠️ Important - Node.js Version Maintenance**:

- **Node.js**: This Dockerfile uses Node.js 24.13.0-slim, which was the latest LTS version at the time of writing. To ensure security and stay up-to-date, regularly check and update the `NODE_VERSION` ARG in the Dockerfile to the latest Node.js LTS version. Check the latest version at [Nodejs official website](https://nodejs.org/) and browse available Node.js images on [Docker Hub](https://hub.docker.com/_/node)."""

new_important = """> [!IMPORTANT]
> **Node.js Version Maintenance**:
>
> - **Node.js**: This Dockerfile uses Node.js 24.13.0-slim, which was the latest LTS version at the time of writing. To ensure security and stay up-to-date, regularly check and update the `NODE_VERSION` ARG in the Dockerfile to the latest Node.js LTS version. Check the latest version at [Nodejs official website](https://nodejs.org/) and browse available Node.js images on [Docker Hub](https://hub.docker.com/_/node)."""

content = content.replace(old_important, new_important)

with open("examples/with-docker/README.md", "w") as f:
    f.write(content)

print("with-docker/README.md updated")

# Fix with-docker-export-output README.md
with open("examples/with-docker-export-output/README.md", "r") as f:
    content = f.read()

# Remove checkmark bullets
content = content.replace("- ✅ Multi-stage Docker build for optimal image size", "- Multi-stage Docker build for optimal image size")
content = content.replace("- ✅ Static export: Fully static HTML/CSS/JavaScript site", "- Static export: Fully static HTML/CSS/JavaScript site")
content = content.replace("- ✅ Two serving options: Nginx (production-grade) and serve (simple Node.js server)", "- Two serving options: Nginx (production-grade) and serve (simple Node.js server)")
content = content.replace("- ✅ Security best practices (non-root user)", "- Security best practices (non-root user)")
content = content.replace("- ✅ Slim/Alpine Linux base images for optimal compatibility and smaller size", "- Slim/Alpine Linux base images for optimal compatibility and smaller size")
content = content.replace("- ✅ BuildKit cache mounts for faster builds", "- BuildKit cache mounts for faster builds")
content = content.replace("- ✅ Production-ready configuration with optimized Nginx settings", "- Production-ready configuration with optimized Nginx settings")
content = content.replace("- ✅ Docker Compose support for easy deployment", "- Docker Compose support for easy deployment")

# Convert Important section to GitHub callout
old_important = """**⚠️ Important - Version Maintenance**:


- **Node.js**: This Dockerfile uses Node.js 24.13.0-slim, which was the latest LTS version at the time of writing. To ensure security and stay up-to-date, regularly check and update the `NODE_VERSION` ARG in the Dockerfile to the latest Node.js LTS version. Check the latest version at [Node.js official website](https://nodejs.org/) and browse available Node.js images on [Docker Hub](https://hub.docker.com/_/node).


- **Nginx**: The Nginx Dockerfile uses `nginxinc/nginx-unprivileged:alpine3.22`. Regularly check and update the `NGINXINC_IMAGE_TAG` ARG to the latest version. Browse available Nginx images on [Docker Hub](https://hub.docker.com/r/nginxinc/nginx-unprivileged).


- **serve package**: The serve Dockerfile uses `serve@14.2.5`. Update to the latest version as needed for bug fixes and features."""

new_important = """> [!IMPORTANT]
> **Version Maintenance**:
>
> - **Node.js**: This Dockerfile uses Node.js 24.13.0-slim, which was the latest LTS version at the time of writing. To ensure security and stay up-to-date, regularly check and update the `NODE_VERSION` ARG in the Dockerfile to the latest Node.js LTS version. Check the latest version at [Node.js official website](https://nodejs.org/) and browse available Node.js images on [Docker Hub](https://hub.docker.com/_/node).
> - **Nginx**: The Nginx Dockerfile uses `nginxinc/nginx-unprivileged:alpine3.22`. Regularly check and update the `NGINXINC_IMAGE_TAG` ARG to the latest version. Browse available Nginx images on [Docker Hub](https://hub.docker.com/r/nginxinc/nginx-unprivileged).
> - **serve package**: The serve Dockerfile uses `serve@14.2.5`. Update to the latest version as needed for bug fixes and features."""

content = content.replace(old_important, new_important)

with open("examples/with-docker-export-output/README.md", "w") as f:
    f.write(content)

print("with-docker-export-output/README.md updated")

# Fix Dockerfile
with open("examples/with-docker/Dockerfile", "r") as f:
    content = f.read()

# Remove cache mount from build stage and add comments
old_build = """# Build Next.js application
RUN --mount=type=cache,target=/app/.next/cache \\
  if [ -f package-lock.json ]; then \\
    npm run build; \\
  elif [ -f yarn.lock ]; then \\
    corepack enable yarn && yarn build; \\
  elif [ -f pnpm-lock.yaml ]; then \\
    corepack enable pnpm && pnpm build; \\
  else \\
    echo "No lockfile found." && exit 1; \\
  fi"""

new_build = """# If you want to speed up Docker rebuilds, you can cache the build artifacts
# by adding: --mount=type=cache,target=/app/.next/cache
# This caches the .next/cache directory across builds, but it also prevents
# .next/cache/fetch-cache from being included in the final image, meaning
# cached fetch responses from the build won't be available at runtime.
RUN if [ -f package-lock.json ]; then \\
    npm run build; \\
  elif [ -f yarn.lock ]; then \\
    corepack enable yarn && yarn build; \\
  elif [ -f pnpm-lock.yaml ]; then \\
    corepack enable pnpm && pnpm build; \\
  else \\
    echo "No lockfile found." && exit 1; \\
  fi"""

content = content.replace(old_build, new_build)

# Add .next directory creation and fetch cache comment in runner stage (combined RUN to satisfy hadolint)
old_runner = """# Copy production assets
COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static

# Switch to non-root user for security best practices
USER node"""

new_runner = """# Copy production assets
COPY --from=builder --chown=node:node /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next && chown node:node .next

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static

# If you want to persist the fetch cache generated during the build so that
# cached responses are available immediately on startup, uncomment this line:
# COPY --from=builder --chown=node:node /app/.next/cache ./.next/cache

# Switch to non-root user for security best practices
USER node"""

content = content.replace(old_runner, new_runner)

with open("examples/with-docker/Dockerfile", "w") as f:
    f.write(content)

print("Dockerfile updated")

# Fix Dockerfile.bun
with open("examples/with-docker/Dockerfile.bun", "r") as f:
    content = f.read()

# Add .next directory creation and fetch cache comment in runner stage (combined RUN)
old_runner_bun = """# Copy production assets
COPY --from=builder --chown=bun:bun /app/public ./public
COPY --from=builder --chown=bun:bun /app/.next/standalone ./
COPY --from=builder --chown=bun:bun /app/.next/static ./.next/static

# Switch to non-root user for security best practices
USER bun"""

new_runner_bun = """# Copy production assets
COPY --from=builder --chown=bun:bun /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next && chown bun:bun .next

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=bun:bun /app/.next/standalone ./
COPY --from=builder --chown=bun:bun /app/.next/static ./.next/static

# If you want to persist the fetch cache generated during the build so that
# cached responses are available immediately on startup, uncomment this line:
# COPY --from=builder --chown=bun:bun /app/.next/cache ./.next/cache

# Switch to non-root user for security best practices
USER bun"""

content = content.replace(old_runner_bun, new_runner_bun)

with open("examples/with-docker/Dockerfile.bun", "w") as f:
    f.write(content)

print("Dockerfile.bun updated")

PYTHON

echo "Patch applied successfully."

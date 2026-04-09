#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'Set the correct permission for prerender cache' examples/with-docker/Dockerfile 2>/dev/null && \
   grep -q 'Set the correct permission for prerender cache' examples/with-docker/Dockerfile.bun 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# =============================================================================
# Fix Dockerfile - remove cache mount, add mkdir/chown
# =============================================================================

# Remove the BuildKit cache mount line and preceding backslash
sed -i 's/RUN --mount=type=cache,target=\/app\/.next\/cache \\/# Build Next.js application\n# If you want to speed up Docker rebuilds, you can cache the build artifacts\n# by adding: --mount=type=cache,target=\/app\/.next\/cache\n# This caches the .next\/cache directory across builds, but it also prevents\n# .next\/cache\/fetch-cache from being included in the final image, meaning\n# cached fetch responses from the build won'\''t be available at runtime.\nRUN/g' examples/with-docker/Dockerfile

# Handle the case where it might not have the backslash continuation
sed -i 's/RUN --mount=type=cache,target=\/app\/.next\/cache \\//g' examples/with-docker/Dockerfile
sed -i 's/RUN --mount=type=cache,target=\/app\/.next\/cache$/# Build Next.js application\n# If you want to speed up Docker rebuilds, you can cache the build artifacts\n# by adding: --mount=type=cache,target=\/app\/.next\/cache\n# This caches the .next\/cache directory across builds, but it also prevents\n# .next\/cache\/fetch-cache from being included in the final image, meaning\n# cached fetch responses from the build won'\''t be available at runtime.\nRUN/g' examples/with-docker/Dockerfile

# Use a Python script for more complex multi-line edits
cat > /tmp/fix_dockerfile.py << 'PYEOF'
import re
from pathlib import Path

dockerfile = Path("examples/with-docker/Dockerfile")
content = dockerfile.read_text()

# Fix the RUN command - remove cache mount and add comments
old_build = """# Build Next.js application
RUN --mount=type=cache,target=/app/.next/cache \\
  if [ -f package-lock.json ]; then"""

new_build = """# Build Next.js application
# If you want to speed up Docker rebuilds, you can cache the build artifacts
# by adding: --mount=type=cache,target=/app/.next/cache
# This caches the .next/cache directory across builds, but it also prevents
# .next/cache/fetch-cache from being included in the final image, meaning
# cached fetch responses from the build won't be available at runtime.
RUN if [ -f package-lock.json ]; then"""

content = content.replace(old_build, new_build)

# Fix the runner stage - add mkdir/chown and optional cache copy comment
old_runner = """# Copy production assets
COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static

# Switch to non-root user for security best practices
USER node"""

new_runner = """# Copy production assets
COPY --from=builder --chown=node:node /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown node:node .next

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

dockerfile.write_text(content)
print("Dockerfile updated")
PYEOF

python3 /tmp/fix_dockerfile.py

# =============================================================================
# Fix Dockerfile.bun - add mkdir/chown
# =============================================================================

cat > /tmp/fix_dockerfile_bun.py << 'PYEOF'
import re
from pathlib import Path

dockerfile = Path("examples/with-docker/Dockerfile.bun")
content = dockerfile.read_text()

# Fix the runner stage - add mkdir/chown and optional cache copy comment
old_runner = """# Copy production assets
COPY --from=builder --chown=bun:bun /app/public ./public
COPY --from=builder --chown=bun:bun /app/.next/standalone ./
COPY --from=builder --chown=bun:bun /app/.next/static ./.next/static

# Switch to non-root user for security best practices
USER bun"""

new_runner = """# Copy production assets
COPY --from=builder --chown=bun:bun /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown bun:bun .next

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=bun:bun /app/.next/standalone ./
COPY --from=builder --chown=bun:bun /app/.next/static ./.next/static

# If you want to persist the fetch cache generated during the build so that
# cached responses are available immediately on startup, uncomment this line:
# COPY --from=builder --chown=bun:bun /app/.next/cache ./.next/cache

# Switch to non-root user for security best practices
USER bun"""

content = content.replace(old_runner, new_runner)

dockerfile.write_text(content)
print("Dockerfile.bun updated")
PYEOF

python3 /tmp/fix_dockerfile_bun.py

# =============================================================================
# Fix README.md - update documentation
# =============================================================================

cat > /tmp/fix_readme.py << 'PYEOF'
from pathlib import Path

readme = Path("examples/with-docker/README.md")
content = readme.read_text()

# Update Features list - remove emoji bullets
content = content.replace(
    """- ✅ Multi-stage Docker build for optimal image size
- ✅ Next.js standalone mode for minimal production builds
- ✅ Security best practices (non-root user)
- ✅ Slim Linux base image for optimal compatibility and smaller size
- ✅ BuildKit cache mounts for faster builds
- ✅ Production-ready configuration""",
    """- Multi-stage Docker build for optimal image size
- Next.js standalone mode for minimal production builds
- Security best practices (non-root user)
- Slim Linux base image for optimal compatibility and smaller size
- BuildKit cache mounts for faster builds
- Production-ready configuration"""
)

# Update BuildKit cache mounts description
content = content.replace(
    """- **BuildKit cache mounts**: Speeds up builds by caching package manager stores (`/root/.npm`, `/usr/local/share/.cache/yarn`, `/root/.local/share/pnpm/store`) and Next.js build cache (`/app/.next/cache`)""",
    """- **BuildKit cache mounts**: Speeds up builds by caching package manager stores (`/root/.npm`, `/usr/local/share/.cache/yarn`, `/root/.local/share/pnpm/store`). See the Dockerfile for an optional `.next/cache` mount to speed up rebuilds."""
)

# Add writable .next directory line after standalone output
content = content.replace(
    """- **Standalone output**: Copies only the necessary files from `.next/standalone` and `.next/static`
- **Node.js version maintenance""",
    """- **Standalone output**: Copies only the necessary files from `.next/standalone` and `.next/static`
- **Writable `.next` directory**: The `.next` directory is created and owned by the `node` user so the server can write prerender cache and optimized images at runtime
- **Node.js version maintenance"""
)

# Update Dockerfile.bun standalone output description
content = content.replace(
    """- **Standalone output**: Same optimized output as the Node.js version

**Why Node.js slim image tag?**""",
    """- **Standalone output**: Same optimized output as the Node.js version, with writable `.next` directory for runtime cache

**Why Node.js slim image tag?**"""
)

# Update Version Maintenance warning to [!IMPORTANT] format
content = content.replace(
    """**⚠️ Important - Node.js Version Maintenance**: This Dockerfile uses Node.js 24.13.0-slim, which was the latest LTS version at the time of writing. To ensure security and stay up-to-date, regularly check and update the `NODE_VERSION` ARG in the Dockerfile to the latest Node.js LTS version. Check the latest version at [Nodejs official website](https://nodejs.org/) and browse available Node.js images on [Docker Hub](https://hub.docker.com/_/node).""",
    """> [!IMPORTANT]
> **Node.js Version Maintenance**: This Dockerfile uses Node.js 24.13.0-slim, which was the latest LTS version at the time of writing. To ensure security and stay up-to-date, regularly check and update the `NODE_VERSION` ARG in the Dockerfile to the latest Node.js LTS version. Check the latest version at [Nodejs official website](https://nodejs.org/) and browse available Node.js images on [Docker Hub](https://hub.docker.com/_/node)."""
)

readme.write_text(content)
print("README.md updated")
PYEOF

python3 /tmp/fix_readme.py

# =============================================================================
# Fix with-docker-export-output/README.md
# =============================================================================

cat > /tmp/fix_export_readme.py << 'PYEOF'
from pathlib import Path

readme = Path("examples/with-docker-export-output/README.md")
content = readme.read_text()

# Update Features list - remove emoji bullets
content = content.replace(
    """- ✅ Multi-stage Docker build for optimal image size
- ✅ Static export: Fully static HTML/CSS/JavaScript site
- ✅ Two serving options: Nginx (production-grade) and serve (simple Node.js server)
- ✅ Security best practices (non-root user)
- ✅ Slim/Alpine Linux base images for optimal compatibility and smaller size
- ✅ BuildKit cache mounts for faster builds
- ✅ Production-ready configuration with optimized Nginx settings
- ✅ Docker Compose support for easy deployment""",
    """- Multi-stage Docker build for optimal image size
- Static export: Fully static HTML/CSS/JavaScript site
- Two serving options: Nginx (production-grade) and serve (simple Node.js server)
- Security best practices (non-root user)
- Slim/Alpine Linux base images for optimal compatibility and smaller size
- BuildKit cache mounts for faster builds
- Production-ready configuration with optimized Nginx settings
- Docker Compose support for easy deployment"""
)

# Update Version Maintenance warning to [!IMPORTANT] format
content = content.replace(
    """**⚠️ Important - Version Maintenance**:

- **Node.js**: This Dockerfile uses Node.js 24.13.0-slim, which was the latest LTS version at the time of writing. To ensure security and stay up-to-date, regularly check and update the `NODE_VERSION` ARG in the Dockerfile to the latest Node.js LTS version. Check the latest version at [Node.js official website](https://nodejs.org/) and browse available Node.js images on [Docker Hub](https://hub.docker.com/_/node).

- **Nginx**: The Nginx Dockerfile uses `nginxinc/nginx-unprivileged:alpine3.22`. Regularly check and update the `NGINXINC_IMAGE_TAG` ARG to the latest version. Browse available Nginx images on [Docker Hub](https://hub.docker.com/r/nginxinc/nginx-unprivileged).

- **serve package**: The serve Dockerfile uses `serve@14.2.5`. Update to the latest version as needed for bug fixes and features.""",
    """> [!IMPORTANT]
> **Version Maintenance**:
>
> - **Node.js**: This Dockerfile uses Node.js 24.13.0-slim, which was the latest LTS version at the time of writing. To ensure security and stay up-to-date, regularly check and update the `NODE_VERSION` ARG in the Dockerfile to the latest Node.js LTS version. Check the latest version at [Node.js official website](https://nodejs.org/) and browse available Node.js images on [Docker Hub](https://hub.docker.com/_/node).
> - **Nginx**: The Nginx Dockerfile uses `nginxinc/nginx-unprivileged:alpine3.22`. Regularly check and update the `NGINXINC_IMAGE_TAG` ARG to the latest version. Browse available Nginx images on [Docker Hub](https://hub.docker.com/r/nginxinc/nginx-unprivileged).
> - **serve package**: The serve Dockerfile uses `serve@14.2.5`. Update to the latest version as needed for bug fixes and features."""
)

readme.write_text(content)
print("with-docker-export-output/README.md updated")
PYEOF

python3 /tmp/fix_export_readme.py

echo "Patch applied successfully."

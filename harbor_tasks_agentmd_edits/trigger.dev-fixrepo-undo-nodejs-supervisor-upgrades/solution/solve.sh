#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trigger.dev

# Idempotent: skip if already applied
if grep -q 'Docker Image Guidelines' CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index ccfc26d3fd7..acc59359707 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -133,6 +133,15 @@ For testable code, **never import env.server.ts** in test files. Pass configurat

 The codebase is transitioning from the "legacy run engine" (spread across codebase) to "Run Engine 2.0" (`@internal/run-engine`). Focus on Run Engine 2.0 for new work.

+## Docker Image Guidelines
+
+When updating Docker image references in `docker/Dockerfile` or other container files:
+
+- **Always use multiplatform/index digests**, not architecture-specific digests
+- Architecture-specific digests (e.g., for `linux/amd64` only) will cause CI failures on different build environments
+- On Docker Hub, the multiplatform digest is shown on the main image page, while architecture-specific digests are listed under "OS/ARCH"
+- Example: Use `node:20.20-bullseye-slim@sha256:abc123...` where the digest is from the multiplatform index, not from a specific OS/ARCH variant
+
 ## Database Migrations (PostgreSQL)

 1. Edit `internal-packages/database/prisma/schema.prisma`
diff --git a/apps/supervisor/.nvmrc b/apps/supervisor/.nvmrc
index 42a1c98ac5a..dc0bb0f4398 100644
--- a/apps/supervisor/.nvmrc
+++ b/apps/supervisor/.nvmrc
@@ -1 +1 @@
-v22.22.0
+v22.12.0
diff --git a/apps/supervisor/Containerfile b/apps/supervisor/Containerfile
index 58dd1ceb409..d5bb5862e96 100644
--- a/apps/supervisor/Containerfile
+++ b/apps/supervisor/Containerfile
@@ -1,4 +1,4 @@
-FROM node:22.22.0-alpine@sha256:bcccf7410b77ca7447d292f616c7b0a89deff87e335fe91352ea04ce8babf50f AS node-22-alpine
+FROM node:22-alpine@sha256:9bef0ef1e268f60627da9ba7d7605e8831d5b56ad07487d24d1aa386336d1944 AS node-22-alpine

 WORKDIR /app

diff --git a/docker/Dockerfile b/docker/Dockerfile
index 60ed0809b6f..a6444bc7633 100644
--- a/docker/Dockerfile
+++ b/docker/Dockerfile
@@ -1,4 +1,4 @@
-ARG NODE_IMAGE=node:20.20.0-bullseye-slim@sha256:f52726bba3d47831859be141b4a57d3f7b93323f8fddfbd8375386e2c3b72319
+ARG NODE_IMAGE=node:20.20-bullseye-slim@sha256:d6c3903e556d4161f63af4550e76244908b6668e1a7d2983eff4873a0c2b0413

 FROM golang:1.23-alpine AS goose_builder
 RUN go install github.com/pressly/goose/v3/cmd/goose@latest

PATCH

echo "Patch applied successfully."

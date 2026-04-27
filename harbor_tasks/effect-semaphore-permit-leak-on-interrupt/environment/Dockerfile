FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates curl python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Pinned tooling
RUN npm install -g pnpm@10.17.1
RUN pip install --break-system-packages --no-cache-dir pytest==8.3.4

WORKDIR /workspace

# Clone Effect repo at base commit (parent of the merge commit for PR #6081)
ARG REPO_URL=https://github.com/Effect-TS/effect.git
ARG BASE_COMMIT=4eb5c008dfc7d2a97b191ca608948d994a2cce4c
RUN git clone --filter=blob:none "$REPO_URL" effect \
 && cd effect \
 && git checkout "$BASE_COMMIT" \
 && git config user.email scaffold@local \
 && git config user.name scaffold

WORKDIR /workspace/effect

# Pre-install dependencies for the workspace.
# Network is needed only at build time; tests run offline.
RUN pnpm config set store-dir /pnpm-store && \
    pnpm install --frozen-lockfile --prefer-offline 2>&1 | tail -40

# Drop a regression test file that exercises the bug.
# It lives in the existing test directory so vitest discovers it.
COPY leak_regression.test.ts /workspace/effect/packages/effect/test/Effect/leak_regression.test.ts

RUN mkdir -p /logs/verifier

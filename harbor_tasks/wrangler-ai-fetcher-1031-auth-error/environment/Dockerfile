FROM node:22.13.1-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

RUN npm install -g pnpm@10.33.0 && pnpm config set store-dir /root/.pnpm-store

WORKDIR /workspace

ARG REPO_URL=https://github.com/cloudflare/workers-sdk.git
ARG BASE_COMMIT=266c418138f4ab53ea662fa45d3e66d38fdf0d52
RUN git clone --filter=blob:none "$REPO_URL" workers-sdk \
    && cd workers-sdk \
    && git fetch --depth 1 origin "$BASE_COMMIT" \
    && git checkout "$BASE_COMMIT"

WORKDIR /workspace/workers-sdk

# Install all workspace dependencies. Wrangler's tests need miniflare,
# workers-utils, undici, msw, vitest, etc. resolved in the workspace.
RUN pnpm install --frozen-lockfile --prefer-offline 2>&1 | tail -30

# wrangler's vitest config resolves several workspace packages via their
# built dist/ artifacts (e.g. @cloudflare/workers-utils, miniflare). Build
# all of wrangler's transitive workspace dependencies so the test runner can
# resolve them. Build cache is left in place so re-runs are fast.
RUN pnpm build --filter "wrangler^..." 2>&1 | tail -20

RUN mkdir -p /logs/verifier

WORKDIR /workspace/workers-sdk

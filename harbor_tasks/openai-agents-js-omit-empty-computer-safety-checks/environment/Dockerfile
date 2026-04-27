FROM node:22.18.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Pin pnpm to the version declared in the repo's package.json (packageManager).
# corepack 0.31 (bundled with node 22.11) has a signing-key mismatch for newer
# pnpm releases; install pnpm directly via npm to dodge it.
RUN npm install -g pnpm@10.32.1

# Pinned Python deps for the verifier harness.
RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace

ARG REPO_URL=https://github.com/openai/openai-agents-js.git
ARG BASE_COMMIT=36a368b7d477f5592aea21aab83b940533607939

RUN git clone --filter=blob:none "$REPO_URL" openai-agents-js \
    && cd openai-agents-js \
    && git checkout "$BASE_COMMIT"

WORKDIR /workspace/openai-agents-js

# Install JS deps at build time so test runs do not need network access.
# Skip lifecycle scripts (postinstall builds, husky hooks) that would try to
# touch a git working tree we do not need at test time.
ENV CI=1 \
    HUSKY=0 \
    PUPPETEER_SKIP_DOWNLOAD=1 \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
RUN pnpm install --frozen-lockfile --ignore-scripts

# Workspace packages reference each other through dist/. Build them now so
# `@openai/agents-core` (and friends) resolve at test time without network.
# Skip the docs subproject — it only matters for the docs site, drags in
# Astro/Starlight, and is not needed for agents-openai unit tests.
# Use the root-level tsc-multi build so each @openai/* package emits both
# CJS (.js) and ESM (.mjs) outputs that the package "exports" map points
# to. A plain `pnpm -F <pkg> run build` only invokes `tsc` and leaves the
# .mjs files missing, which breaks vite-node import resolution.
RUN pnpm -F "@openai/*" run prebuild \
    && pnpm exec tsc-multi --maxWorkers 1

RUN mkdir -p /logs/verifier

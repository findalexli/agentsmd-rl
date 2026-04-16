FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl nodejs npm patch \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g pnpm

WORKDIR /workspace

# Clone the repo (shallow)
RUN git clone --filter=blob:none --depth=1 https://github.com/cloudflare/workers-sdk.git workers-sdk

WORKDIR /workspace/workers-sdk

# Checkout the base commit
RUN git checkout 71259391f84a4df6958936e37b30e7f1faa2fee1

# Install pnpm dependencies only (skip oclog, turbo, etc.)
RUN corepack enable && pnpm install --frozen-lockfile

# Build miniflare package
RUN pnpm run build --filter miniflare

# Create logs directory
RUN mkdir -p /logs/verifier

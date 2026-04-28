FROM node:22-slim

RUN corepack enable && corepack prepare pnpm@9 --activate

# Install git and Python for test harness
RUN apt-get update && apt-get install -y --no-install-recommends git python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /usr/lib/python3.*/EXTERNALLY-MANAGED

WORKDIR /workspace

# Clone the repo at the base commit
RUN git clone --filter=blob:none --no-checkout https://github.com/cloudflare/workers-sdk.git /workspace/workers-sdk && \
    cd /workspace/workers-sdk && \
    git checkout 4ca7cc6afb7a7cbf0e42580801654803b406b1e0

# Install dependencies
WORKDIR /workspace/workers-sdk
RUN pnpm install --frozen-lockfile 2>&1 || pnpm install --no-frozen-lockfile 2>&1

# Build workspace packages needed by wrangler
RUN pnpm run build --filter @cloudflare/workers-utils --filter miniflare

RUN mkdir -p /logs/verifier

WORKDIR /workspace/workers-sdk

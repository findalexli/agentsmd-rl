FROM node:22-slim

# Install pnpm and tsx globally (pnpm must match the repo's packageManager + engines.pnpm)
RUN npm install -g pnpm@10.33.0 tsx@4.19.2

# Install Python for test harness
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip git && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest==8.3.4 --break-system-packages

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/cloudflare/workers-sdk.git && \
    cd workers-sdk && \
    git checkout 525a46bca7c9a8a57972ac152ab9c400df0bf186

# Install monorepo dependencies filtered to the affected package
WORKDIR /workspace/workers-sdk
RUN pnpm install --frozen-lockfile --filter @cloudflare/local-explorer-ui

RUN mkdir -p /logs/verifier

WORKDIR /workspace/workers-sdk

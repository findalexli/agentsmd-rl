FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest pytest-timeout --break-system-packages --quiet

RUN npm install -g pnpm@10

WORKDIR /workspace

# Clone monorepo with filter to skip blob downloads (only metadata)
RUN git clone --depth=1 --filter=blob:none \
    --filter=blob:none \
    --depth=100 \
    https://github.com/openai/openai-agents-js \
    openai-agents-js

WORKDIR /workspace/openai-agents-js
# Checkout the base commit
RUN git checkout 36a368b7d477f5592aea21aab83b940533607939

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build all packages (agents-core is a dependency of agents-openai)
RUN pnpm build

RUN mkdir -p /logs/verifier

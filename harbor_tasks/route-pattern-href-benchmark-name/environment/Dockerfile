FROM node:24-slim

ENV CI=true

RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Pre-install pytest in Docker build (avoids externally-managed-environment)
RUN pip3 install --break-system-packages pytest==8.3.4

RUN npm install -g pnpm@10.26.0

WORKDIR /workspace/remix

# Shallow clone the repo at the base commit
RUN git clone --depth=1 https://github.com/remix-run/remix.git /workspace/remix \
    && git fetch --depth=1 origin a2245eab8257758f5e323a5a4e3c89386568e3bb \
    && git checkout a2245eab8257758f5e323a5a4e3c89386568e3bb

# Install workspace dependencies (needed for typecheck + format)
RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier

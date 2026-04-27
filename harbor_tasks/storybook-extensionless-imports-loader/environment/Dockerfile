FROM node:22.16-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir pytest==8.3.4

WORKDIR /workspace/repo

COPY repo/package.json ./package.json
COPY repo/tsconfig.json ./tsconfig.json
COPY repo/vitest.config.ts ./vitest.config.ts
COPY repo/shims/ ./shims/

RUN npm install --no-audit --no-fund --prefer-offline=false

COPY repo/code/ ./code/

RUN mkdir -p /logs/verifier

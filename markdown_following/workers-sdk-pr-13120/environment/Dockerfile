FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages pytest==8.3.4

RUN mkdir -p /logs/verifier

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/cloudflare/workers-sdk.git /workspace/workers-sdk \
    && cd /workspace/workers-sdk \
    && git fetch --filter=blob:none origin e200179d8dbdb36d716e5df9e981b3219c93d974 \
    && git checkout FETCH_HEAD

RUN corepack enable pnpm \
    && cd /workspace/workers-sdk \
    && pnpm install --frozen-lockfile

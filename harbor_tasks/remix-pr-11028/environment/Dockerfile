FROM node:24-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@10.26.0 --activate

WORKDIR /workspace/remix

RUN git clone --filter=blob:none https://github.com/remix-run/remix.git . \
    && git checkout 35f35e82b26381f7f402d5d75db3b60e5329fb6c

RUN pnpm install 2>&1 | tail -20

RUN pip install --break-system-packages pytest==8.3.4

RUN mkdir -p /logs/verifier

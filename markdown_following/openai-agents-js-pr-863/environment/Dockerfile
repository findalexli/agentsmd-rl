FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@10.7.0 --activate

RUN pip3 install --break-system-packages pytest==8.3.4

RUN mkdir -p /logs/verifier

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git checkout f0ad7065c8ec8c532bf702d1912b7d42ee17b141

WORKDIR /workspace/openai-agents-js

RUN pnpm install --frozen-lockfile

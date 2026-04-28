FROM node:22-slim

RUN apt-get update && apt-get install -y git python3 python3-pip curl --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@10.14.0 --activate

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git checkout 2260e211926624c0bcd89497a8b180724b14d720

WORKDIR /workspace/openai-agents-js

RUN pnpm install --frozen-lockfile

RUN pnpm prebuild && pnpm build

RUN mkdir -p /logs/verifier

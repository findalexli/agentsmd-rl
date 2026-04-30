FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@10.28.0 --activate

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js \
    && cd /workspace/openai-agents-js \
    && git checkout 4a53e998a2cd27eb004c4c25d6d178bfe371b72e

WORKDIR /workspace/openai-agents-js
RUN pnpm install --frozen-lockfile

RUN pip install --break-system-packages pytest==8.3.4

RUN mkdir -p /logs/verifier

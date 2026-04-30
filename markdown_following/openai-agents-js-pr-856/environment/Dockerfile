FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages pytest==8.3.4

RUN corepack enable && corepack prepare pnpm@10.28.0 --activate

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js \
    && cd /workspace/openai-agents-js \
    && git checkout 47d10c0dabd3f179b5d59e7eb9c5eefcec93a98f \
    && pnpm install

RUN mkdir -p /tests
WORKDIR /workspace/openai-agents-js
RUN mkdir -p /logs/verifier

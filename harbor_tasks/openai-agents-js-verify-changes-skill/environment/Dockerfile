FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --break-system-packages pytest==8.3.4

RUN corepack enable && corepack prepare pnpm@10 --activate

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js \
    && cd /workspace/openai-agents-js \
    && git checkout b54fc4a3222ea8b14b1c3a8e45457b4905354bee \
    && pnpm i \
    && pnpm build

RUN mkdir -p /logs/verifier
WORKDIR /workspace/openai-agents-js

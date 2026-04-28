FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages pytest==8.3.4 pytest-json-ctrf==0.3.0

RUN corepack enable && corepack prepare pnpm@10.28.0 --activate

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js

WORKDIR /workspace/openai-agents-js

RUN git checkout 60a48d71be74bcdf35646b1e1fb84bde7445e8dd

RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier

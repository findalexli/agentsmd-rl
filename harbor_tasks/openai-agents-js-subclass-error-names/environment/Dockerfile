FROM node:22.14.0-slim

ENV CI=1 \
    DEBIAN_FRONTEND=noninteractive \
    HUSKY=0 \
    PNPM_HOME=/root/.local/share/pnpm \
    PATH=/root/.local/share/pnpm:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.3.5
ENV PATH=/opt/venv/bin:$PATH

RUN corepack enable \
    && corepack prepare pnpm@10.28.0 --activate

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git openai-agents-js \
    && cd openai-agents-js \
    && git checkout 4a53e998a2cd27eb004c4c25d6d178bfe371b72e

WORKDIR /workspace/openai-agents-js

RUN pnpm install --frozen-lockfile

RUN pnpm build

RUN mkdir -p /logs/verifier

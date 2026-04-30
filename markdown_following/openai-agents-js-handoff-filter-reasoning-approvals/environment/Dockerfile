FROM node:22.20.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PNPM_HOME=/root/.local/share/pnpm \
    PATH=/root/.local/share/pnpm:$PATH \
    CI=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1
ENV PATH=/opt/venv/bin:$PATH

RUN npm install -g pnpm@10.32.1

RUN git init /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git remote add origin https://github.com/openai/openai-agents-js.git && \
    git fetch --depth=1 origin ae6444ead1c6d68ee74185f6d822bc16691cd32d && \
    git checkout FETCH_HEAD

WORKDIR /workspace/openai-agents-js

RUN pnpm install --frozen-lockfile \
    && pnpm build:ci \
    && mkdir -p node_modules/@openai \
    && ln -sf ../../packages/agents-core node_modules/@openai/agents-core \
    && ln -sf ../../packages/agents-openai node_modules/@openai/agents-openai \
    && ln -sf ../../packages/agents-realtime node_modules/@openai/agents-realtime \
    && ln -sf ../../packages/agents-extensions node_modules/@openai/agents-extensions \
    && ln -sf ../../packages/agents node_modules/@openai/agents \
    && pnpm store prune

RUN mkdir -p /logs/verifier

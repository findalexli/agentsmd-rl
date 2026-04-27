FROM node:22.13.1-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
    CI=1 \
    NODE_ENV=test

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        curl \
        jq \
    && rm -rf /var/lib/apt/lists/*

# corepack's signature keys bundled with node:22.13 are stale; bypass them so
# the pnpm@10.30.3 download succeeds.
ENV COREPACK_INTEGRITY_KEYS=0
RUN corepack enable && corepack prepare pnpm@10.30.3 --activate

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git init /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git remote add origin https://github.com/openai/openai-agents-js.git && \
    git fetch --depth=1 origin 82d9a3b6a62ba1c7739d9b1c5800edf91ce22a19 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/openai-agents-js

RUN pnpm install --frozen-lockfile

RUN pnpm build

RUN mkdir -p /logs/verifier

FROM node:22.14.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@10.17.1

WORKDIR /workspace

RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin a03b6a29ed0b983b0440b8ef4be47f47c57d73d7 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect

RUN pnpm config set store-dir /pnpm-store \
    && pnpm install --filter '@effect/sql-kysely...' --frozen-lockfile

RUN pip3 install --break-system-packages --no-cache-dir pytest==8.3.4

RUN mkdir -p /logs/verifier

WORKDIR /workspace/effect/packages/sql-kysely

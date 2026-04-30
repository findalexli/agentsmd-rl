FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH="$PNPM_HOME:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    curl \
    python3 \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@10.17.1 --activate

RUN pip3 install --no-cache-dir --break-system-packages \
    pytest==8.3.4 \
    pytest-json-report==1.5.0

WORKDIR /workspace
RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin ed4531817716dbf52e1d59ac4d3614ef5a1dae71 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect
RUN pnpm install --frozen-lockfile --prefer-offline

RUN mkdir -p /logs/verifier

WORKDIR /workspace/effect

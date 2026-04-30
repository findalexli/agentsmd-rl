FROM node:24-slim

ENV CI=1
ENV PNPM_HOME=/usr/local/pnpm
ENV PATH=$PNPM_HOME:$PATH
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        python3 \
        python3-pip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

RUN corepack enable && corepack prepare pnpm@10.26.0 --activate

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/remix-run/remix.git remix \
    && cd remix \
    && git checkout 7a028b5a1cccb5b231f6b908da2aa06a95000a7f

WORKDIR /workspace/remix
# Install deps for route-pattern + its bench/ workspace (which is picked up by
# tsgo via the package's tsconfig.json). Without bench's deps installed,
# `pnpm typecheck` errors on missing `vitest`, `find-my-way`, etc.
RUN pnpm install \
        --filter "@remix-run/route-pattern..." \
        --filter "route-pattern-bench..." \
        --frozen-lockfile --ignore-scripts

RUN mkdir -p /logs/verifier

WORKDIR /workspace/remix

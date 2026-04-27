FROM node:22.14.0-slim

# System deps for python pytest harness + git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# pytest harness deps (pinned)
RUN pip install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1 \
        pyyaml==6.0.2

# pnpm (matching repo's packageManager field)
ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH=$PNPM_HOME:$PATH
RUN corepack enable && corepack prepare pnpm@10.17.1 --activate

WORKDIR /workspace

# Clone effect at exact base commit (parent of merge commit f6b0960...)
ARG BASE_COMMIT=88a5260788d57bb0c31a645fa44b5a68f5c73c38
RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin 88a5260788d57bb0c31a645fa44b5a68f5c73c38 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect

# Install workspace deps. --ignore-scripts to skip playwright browser download etc.
# Strict-peer-deps off because the monorepo has known peer warnings.
RUN pnpm install --frozen-lockfile --ignore-scripts --strict-peer-dependencies=false

# Reward dir Harbor expects
RUN mkdir -p /logs/verifier

FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH="$PNPM_HOME:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

RUN npm install --global pnpm@10.17.1

WORKDIR /workspace

RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin 904e055143ad74b1e4cd25429f44e7a3e86db5dc && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect

# Install all monorepo dependencies (workspace install).
# --frozen-lockfile is mandatory for reproducibility.
# --ignore-scripts skips package postinstall scripts so we don't trigger full builds
# of unrelated packages — vitest can run tests directly against the .ts sources.
RUN pnpm install --frozen-lockfile --ignore-scripts

# Pre-warm Vite/esbuild cache so first test invocation is fast.
RUN cd packages/effect && \
    pnpm exec vitest --version

RUN mkdir -p /logs/verifier

FROM node:24-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV CI=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3 /usr/local/bin/python

# pnpm version pinned to match the repo's packageManager field
RUN npm install -g pnpm@9.12.2 corepack@0.31.0

# Test harness deps (pinned)
RUN python3 -m pip install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

ARG TRPC_BASE_COMMIT=59f2cdb3c58310733b06d3b2e16c94065fe0a9c3
RUN git clone --filter=blob:none https://github.com/trpc/trpc.git trpc \
    && cd trpc \
    && git checkout ${TRPC_BASE_COMMIT}

WORKDIR /workspace/trpc

# Run pnpm install (no scripts, no frozen lockfile in case of transient lock drift)
RUN pnpm install --frozen-lockfile --ignore-scripts

# Verify vitest is available via the workspace
RUN node -e "require.resolve('vitest', { paths: ['/workspace/trpc/packages/tests'] })"

RUN mkdir -p /logs/verifier

CMD ["bash"]

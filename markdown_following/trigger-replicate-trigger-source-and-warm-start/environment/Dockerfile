FROM node:20.20.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1 \
        sqlparse==0.5.3

WORKDIR /workspace

ARG REPO_URL=https://github.com/triggerdotdev/trigger.dev.git
ARG BASE_COMMIT=efcafdf388344487681ea388ed6fcfd4e953aa98
RUN git clone --filter=blob:none "$REPO_URL" trigger.dev && \
    cd trigger.dev && \
    git checkout "$BASE_COMMIT" && \
    git config user.email "scaffold@example.com" && \
    git config user.name "scaffold"

# Standalone deps for the test harness — installed in a sibling directory so
# we don't touch the repo's own package.json / pnpm workspace.
WORKDIR /opt/harness
RUN npm init -y --silent >/dev/null 2>&1 && \
    npm install --no-save --no-audit --no-fund --legacy-peer-deps \
        zod@3.25.76 \
        @clickhouse/client@1.12.1 \
        esbuild@0.24.0 \
        prisma@6.14.0

WORKDIR /workspace/trigger.dev

RUN mkdir -p /logs/verifier

CMD ["bash"]

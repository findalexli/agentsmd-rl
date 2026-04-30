FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (filter clone — large monorepo)
RUN git init /workspace/prisma && \
    cd /workspace/prisma && \
    git remote add origin https://github.com/prisma/prisma.git && \
    git fetch --depth=1 origin a60fe90928873bcec23b0fd07a002c164d7f4d27 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prisma

# Install minimal deps for running connection-string.ts with tsx and vitest.
# kleur must be at root (packages/debug imports it).
# mssql + tsx + vitest go in adapter-mssql.
RUN mkdir -p node_modules && cd node_modules && npm pack kleur@4.1.5 2>/dev/null && tar xzf kleur-*.tgz && mv package kleur && rm kleur-*.tgz && cd /workspace/prisma && \
    cd packages/adapter-mssql && \
    echo '{"private":true,"dependencies":{"mssql":"^11.0.1","async-mutex":"0.5.0","tsx":"^4"},"devDependencies":{"vitest":"1.6.1"}}' > /tmp/pkg.json && \
    cp /tmp/pkg.json package.json && \
    npm install && \
    git checkout package.json

# Vitest config with resolve aliases for workspace packages
RUN echo 'import { defineConfig } from "vitest/config";' > /workspace/prisma/packages/adapter-mssql/vitest.config.ts && \
    echo 'export default defineConfig({resolve:{alias:{"@prisma/driver-adapter-utils":"/workspace/prisma/packages/driver-adapter-utils/src/index.ts","@prisma/debug":"/workspace/prisma/packages/debug/src/index.ts"}},});' >> /workspace/prisma/packages/adapter-mssql/vitest.config.ts

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# tsx for running TypeScript directly
RUN npm install -g tsx

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/prisma/prisma.git /workspace/prisma && \
    cd /workspace/prisma && \
    git checkout a60fe90928873bcec23b0fd07a002c164d7f4d27 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prisma

# Install mssql + kleur deps (mssql for connection-string.ts, kleur for @prisma/debug)
RUN mkdir -p /tmp/deps && \
    cd /tmp/deps && \
    npm init -y > /dev/null 2>&1 && \
    npm install mssql@11 kleur --ignore-scripts > /dev/null 2>&1 && \
    mkdir -p /workspace/prisma/packages/adapter-mssql/node_modules && \
    cp -r node_modules/* /workspace/prisma/packages/adapter-mssql/node_modules/ && \
    mkdir -p /workspace/prisma/node_modules && \
    cp -r node_modules/kleur /workspace/prisma/node_modules/kleur && \
    rm -rf /tmp/deps

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

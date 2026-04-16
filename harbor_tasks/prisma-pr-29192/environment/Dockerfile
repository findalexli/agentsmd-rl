FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    python3 \
    python3-pip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@10.33.0

ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH=$PNPM_HOME:$PATH

WORKDIR /workspace

RUN git clone --filter=blob:none --depth=1 https://github.com/prisma/prisma.git prisma \
    && cd prisma \
    && git fetch --depth=1 origin 77bfc96b9f61b0fd8405fc9515707bf8fd9c5c53 \
    && git checkout 77bfc96b9f61b0fd8405fc9515707bf8fd9c5c53

WORKDIR /workspace/prisma

RUN pnpm install --no-frozen-lockfile

RUN mkdir -p /logs/verifier

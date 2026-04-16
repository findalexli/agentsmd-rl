FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest --break-system-packages

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

WORKDIR /workspace/router

RUN git checkout d9e6c3179a888afb5fb47e7b31c31016f446d81f

RUN npm install -g pnpm

RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier

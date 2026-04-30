FROM node:22-slim

RUN apt-get update && apt-get install -y git python3 python3-pip --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@10.17.1

WORKDIR /workspace/effect

RUN git clone --filter=blob:none https://github.com/effect-ts/effect.git . && \
    git checkout 4eb5c008dfc7d2a97b191ca608948d994a2cce4c

RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier

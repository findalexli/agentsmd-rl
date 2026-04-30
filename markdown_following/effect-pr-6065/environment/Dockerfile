FROM node:22-slim

RUN apt-get update && apt-get install -y git python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@10.17.1

WORKDIR /workspace/effect

RUN git init && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin 12b1f1eadf649e30dec581b7351ba3abb12f8004 && \
    git checkout FETCH_HEAD

RUN pnpm install --ignore-scripts 2>&1 | tail -5

RUN mkdir -p /logs/verifier

FROM node:20.19.4-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV YARN_CACHE_FOLDER=/tmp/yarn-cache
ENV CYPRESS_INSTALL_BINARY=0
ENV PUPPETEER_SKIP_DOWNLOAD=1

# System deps: git for cloning, python3+pip for the test harness, build tools for native modules.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        python3 \
        python3-pip \
        ca-certificates \
        build-essential \
        python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages \
        pytest==8.3.4

WORKDIR /workspace

# Shallow clone at the base commit (parent of merge commit 987173b...).
RUN git init /workspace/excalidraw && \
    cd /workspace/excalidraw && \
    git remote add origin https://github.com/excalidraw/excalidraw.git && \
    git fetch --depth=1 origin 81ab857a6fc66254239947524faccf45d5925f69 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/excalidraw

# Install dependencies. excalidraw is a yarn-1 monorepo; --frozen-lockfile keeps versions reproducible.
RUN yarn install --frozen-lockfile --network-timeout 600000

RUN mkdir -p /logs/verifier

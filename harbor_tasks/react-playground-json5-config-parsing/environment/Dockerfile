FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone react repo at base commit
RUN git init /workspace/react && \
    cd /workspace/react && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin 74568e8627aa43469b74f2972f427a209639d0b6 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/react

# Install json5 globally so test scripts can require it (needed after fix is applied)
RUN npm install -g json5@2.2.3
ENV NODE_PATH=/usr/local/lib/node_modules

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

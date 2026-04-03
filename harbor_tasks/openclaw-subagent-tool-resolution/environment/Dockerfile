FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/openclaw && \
    cd /workspace/openclaw && \
    git remote add origin https://github.com/openclaw/openclaw.git && \
    git fetch --depth=1 origin 6883f688e8da11481a5d0f91dfab4e4ba6e9f871 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/openclaw

# Install deps so vitest + tsc work during verification
RUN npm install -g pnpm@10.32.1 && \
    pnpm install --frozen-lockfile

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"
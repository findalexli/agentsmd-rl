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
    git fetch --depth=1 origin 865160e57292bfc32082fa885efe1a48e64bb06c && \
    git checkout FETCH_HEAD

# Install pnpm via corepack and project dependencies (needed for behavioral tests)
RUN corepack enable && corepack prepare pnpm@10.32.1 --activate
RUN cd /workspace/openclaw && pnpm install --frozen-lockfile 2>/dev/null || pnpm install

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/openclaw
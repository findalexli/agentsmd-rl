FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

ARG REPO=https://github.com/anomalyco/opencode.git
ARG COMMIT=1d363fa19fe9c1445f635498da48211bf09cbc97

RUN git clone --filter=blob:none "$REPO" /repo && \
    cd /repo && \
    git checkout "$COMMIT" && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

RUN npm install -g typescript

RUN mkdir -p /logs/verifier

WORKDIR /repo
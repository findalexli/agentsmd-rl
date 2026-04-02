FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

ARG REPO=https://github.com/anomalyco/opencode.git
ARG COMMIT=2d502d6ffe1aaf8c02d26b863ad4fd8d82bf28b5

RUN git clone --filter=blob:none "$REPO" /repo && \
    cd /repo && \
    git checkout "$COMMIT" && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /repo
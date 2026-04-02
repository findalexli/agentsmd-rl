FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

ARG REPO=https://github.com/anomalyco/opencode.git
ARG COMMIT=8446719b13a1c9566bccd206cb522f7e524b1867

RUN git clone "$REPO" /repo && \
    cd /repo && \
    git checkout "$COMMIT" && \
    git config user.email "test@test.com" && \
    git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /repo
FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
ARG REPO_URL=https://github.com/anomalyco/opencode.git
ARG BASE_COMMIT=41b0d03f6afabc30696e9ccbbdbb7c3df34fd404

RUN git clone --filter=blob:none ${REPO_URL} /workspace/opencode \
    && cd /workspace/opencode \
    && git checkout ${BASE_COMMIT} \
    && git config user.email "test@test.com" \
    && git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
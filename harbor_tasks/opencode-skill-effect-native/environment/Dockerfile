FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun (pinned version)
RUN curl -fsSL https://bun.sh/install | bash -s -- bun-v1.3.2
ENV PATH="/root/.bun/bin:${PATH}"

# Clone repo at the base commit (before the fix)
ARG BASE_COMMIT=21023337fa8011568b2570a3bd49fffed842ce86
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

# Install dependencies so CI-level tests can run
RUN cd /workspace/opencode && bun install

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode

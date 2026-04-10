FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
ARG BASE_COMMIT=8e4bab51812fccf3b69713904159a4394b3a29ab
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

# Install Bun (required for typecheck and tests)
RUN curl -fsSL https://bun.sh/install | bash

# Install turbo globally for typecheck
RUN npm install -g turbo@2
ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /workspace/opencode
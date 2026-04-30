FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin af2ccc94ebc632d0014f54ea5c5e6c2e26b5dda5 && \
    git checkout FETCH_HEAD

RUN cd /workspace/opencode && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
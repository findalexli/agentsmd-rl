FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential python3 tmux bc && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
ARG REPO_URL=https://github.com/anomalyco/opencode.git
ARG BASE_COMMIT=26382c6216797e65a1b43dea8646725332f62e07

RUN git clone --filter=blob:none "$REPO_URL" /repo && \
    cd /repo && \
    git checkout "$BASE_COMMIT" && \
    git config user.email "test@test.com" && \
    git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /repo
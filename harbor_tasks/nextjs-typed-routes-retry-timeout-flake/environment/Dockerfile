FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test User"

# Clone repo at base commit (before the fix)
ARG BASE_COMMIT=0090db224d177c51f6d5e45fe1be2527ce04e899
RUN git clone --filter=blob:none --no-checkout https://github.com/vercel/next.js.git /repo && \
    cd /repo && \
    git checkout ${BASE_COMMIT}

RUN mkdir -p /logs/verifier

WORKDIR /repo
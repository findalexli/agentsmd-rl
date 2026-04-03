FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (pre-revert: has the shared calculateUserAgentEmulation)
RUN git init /workspace/playwright && \
    cd /workspace/playwright && \
    git remote add origin https://github.com/microsoft/playwright.git && \
    git fetch --depth=1 origin 346b39c7895a7df03b50b087d503e9f2997fe2e0 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/playwright

# Install deps (skip browser downloads via --ignore-scripts),
# then run build to generate protocol types needed by tsc
RUN npm ci --ignore-scripts 2>&1 | tail -20 && \
    npm run build 2>&1 | tail -10 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Shallow clone at exact base commit (pre-fix)
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin ad65b1bdcf3d10e5213c80bea56a73038bbf1c99 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js

# Configure git for patching
RUN git config user.email "test@test.com" && git config user.name "Test"

# Pre-install pytest for test runner (tests only inspect the test file, not run Next.js)
RUN python3 -m pip install --break-system-packages -q pytest pytest-json-ctrf 2>/dev/null || true
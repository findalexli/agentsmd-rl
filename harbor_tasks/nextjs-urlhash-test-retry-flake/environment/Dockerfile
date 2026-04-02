FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /workspace/next.js && \
    cd /workspace/next.js && \
    git checkout 78f73b27069ffe2dc1ddfb2b16013220d2a86569

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js

# Configure git for potential commits
RUN git config user.email "test@test.com" && \
    git config user.name "Test User"

# No heavy dependency install needed — tests are evaluated via static analysis
# The test file is TypeScript but we only need to parse/check it, not run Playwright
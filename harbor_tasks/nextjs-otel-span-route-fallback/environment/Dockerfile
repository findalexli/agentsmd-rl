FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global advice.detachedHead false

# Clone next.js at the base commit (BEFORE the fix)
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin 3003e17b102699bffca325257ae7be53fda69052 && \
    git checkout FETCH_HEAD

# Configure git user for agent commits
RUN cd /workspace/next.js && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

# No build needed — tests inspect source files only (TS templates).
# Full next.js build requires pnpm bootstrap + ~60s compile time and is
# not needed for verifying the span-naming fix.

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js
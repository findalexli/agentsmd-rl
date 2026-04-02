FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone bun at the base commit (BEFORE the fix)
RUN git clone --no-checkout https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout af24e281ebacd6ac77c0f14b4206599cf4ae1c9f && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun
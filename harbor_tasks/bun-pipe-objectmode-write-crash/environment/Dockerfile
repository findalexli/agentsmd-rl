FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone bun at the base commit (BEFORE the fix)
RUN git clone --no-checkout https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 2d4c2beb23085873380840c9bd18eeca29645843 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

# Install Node.js (needed for behavioral tests that eval extracted JS functions)
RUN curl -fsSL https://nodejs.org/dist/v20.11.0/node-v20.11.0-linux-x64.tar.xz \
    | tar -xJ -C /usr/local --strip-components=1

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun
FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone bun at the base commit (before the fix)
RUN git clone --no-checkout https://github.com/oven-sh/bun.git /repo && \
    cd /repo && \
    git checkout 9e93bfa1b69a2f9b8c05acb15e02c5506dd4cbc8 && \
    git config user.email "test@test.com" && \
    git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /repo
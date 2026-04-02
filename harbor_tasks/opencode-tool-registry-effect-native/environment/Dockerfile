FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git clone https://github.com/anomalyco/opencode.git /workspace/opencode \
    && cd /workspace/opencode \
    && git checkout d2bfa92e7438eb7ac7c4e2d72fca708f27c52ba3 \
    && git config user.email "test@test.com" \
    && git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
ARG BASE_COMMIT=8e4bab51812fccf3b69713904159a4394b3a29ab
RUN git clone https://github.com/anomalyco/opencode.git /workspace/opencode \
    && cd /workspace/opencode \
    && git checkout ${BASE_COMMIT} \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
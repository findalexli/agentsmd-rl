FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Shallow-fetch gradio at base commit (repo is very large)
RUN git init /workspace/gradio \
    && cd /workspace/gradio \
    && git remote add origin https://github.com/gradio-app/gradio.git \
    && git fetch --depth 1 origin ccff8b8cacffe36a270fcea9fc8ba29b78c31c8d \
    && git checkout ccff8b8cacffe36a270fcea9fc8ba29b78c31c8d

# Configure git user
RUN cd /workspace/gradio && \
    git config user.email "test@test.com" && \
    git config user.name "Test"

# Install TypeScript locally so tests can require() it
RUN cd /workspace/gradio && npm install typescript@5 --no-save || true

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio
FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before fix)
RUN git clone --filter=blob:none https://github.com/gradio-app/gradio.git /workspace \
    && cd /workspace \
    && git checkout 424a4e4bcfeace96f7f5a678b56a578ad2002cf4 \
    && git config user.email "test@test.com" \
    && git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Copy test files
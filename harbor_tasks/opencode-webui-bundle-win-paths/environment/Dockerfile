FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Clone repo at base commit (before the fix)
RUN git clone https://github.com/anomalyco/opencode.git /workspace/opencode \
    && cd /workspace/opencode \
    && git checkout b7a06e193952a66a8efa07feb4e105f44bf7ea8b \
    && git config user.email "test@test.com" \
    && git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
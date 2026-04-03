FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential unzip tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Install bun (needed for running test validation)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun \
    && cd /workspace/bun \
    && git checkout e94c3035c6f9d7868fb814cfeaf27b219d00e565

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun

# Configure git for patching
RUN git config user.email "test@test.com" && git config user.name "Test"
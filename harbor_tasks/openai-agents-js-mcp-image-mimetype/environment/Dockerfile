FROM node:22-slim

# Install git for cloning and python3 for test runner
RUN apt-get update && \
    apt-get install -y --no-install-recommends git patch python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Install corepack to enable pnpm
RUN corepack enable && corepack prepare pnpm@10.30.3 --activate

WORKDIR /workspace

# Clone repo at base commit (shallow)
RUN git clone --filter=blob:none --no-tags \
    https://github.com/openai/openai-agents-js.git \
    && cd openai-agents-js \
    && git checkout 6884301505b92105c50b7be203d4cf8193d86577

WORKDIR /workspace/openai-agents-js

# Install dependencies and build
RUN pnpm install --frozen-lockfile 2>&1 | tail -5
RUN pnpm build 2>&1 | tail -5

# Pin pytest for test runner
RUN pip3 install --break-system-packages pytest==8.3.4

# Ensure log directory exists
RUN mkdir -p /logs/verifier

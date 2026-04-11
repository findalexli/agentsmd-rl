# Bun-based TypeScript project
FROM oven/bun:1.2-slim

# Install Python for test runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone at base commit (pre-fix): d4694d058cc590b0f05261a04460034d2fa8541d
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git opencode && \
    cd opencode && \
    git checkout d4694d058cc590b0f05261a04460034d2fa8541d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

# Install dependencies (packages/opencode is the relevant package)
WORKDIR /workspace/opencode/packages/opencode
RUN bun install

# Create log directory for Harbor verifier
RUN mkdir -p /logs/verifier

# Required environment variables (disable native watcher since bindings may not be available in container)
ENV OPENCODE_EXPERIMENTAL_FILEWATCHER=false
ENV OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER=true
ENV NODE_ENV=test

# Copy solution patch into container
COPY solution/full.patch /workspace/solution/

WORKDIR /workspace/opencode

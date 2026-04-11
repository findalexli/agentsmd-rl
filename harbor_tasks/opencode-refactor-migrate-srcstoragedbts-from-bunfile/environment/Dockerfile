# Bun-based TypeScript project
FROM oven/bun:1.2-slim

# Install Python for test runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone at base commit (pre-fix): 6fb4f2a7a5d768c11fafdeae4aa8b5c7fcb46b44
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git opencode && \
    cd opencode && \
    git checkout 6fb4f2a7a5d768c11fafdeae4aa8b5c7fcb46b44 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

# Install dependencies (packages/opencode is the relevant package)
WORKDIR /workspace/opencode/packages/opencode
RUN bun install

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

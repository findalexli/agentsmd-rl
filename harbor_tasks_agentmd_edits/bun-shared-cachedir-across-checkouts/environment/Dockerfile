FROM oven/bun:1.2.4-slim

# Install dependencies for testing and git operations
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-pytest \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Clone the Bun repository at the base commit (pre-fix)
# Using shallow clone for efficiency
RUN git clone --depth 100 --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 485ec522a22b469b336aece8276b507a71665a87

# Install Node dependencies for the build scripts
WORKDIR /workspace/bun
RUN bun install --frozen-lockfile || bun install

# Create logs directory for test outputs
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/bun

FROM node:22-slim

# Install Python for the test runner, git for repo operations, and patch for applying fixes
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the repo at the base commit (with history for git operations)
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout ab46b5ec42296c60dc46d97481f038b8df68ed84

# Install dependencies
WORKDIR /workspace/router
RUN npm install -g pnpm && \
    pnpm install

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/router

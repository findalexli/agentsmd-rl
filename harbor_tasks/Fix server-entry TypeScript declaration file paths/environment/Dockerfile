FROM node:22-slim

# Install Python for pytest runner and other dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt-get/lists/*

# Install pnpm globally
RUN npm install -g pnpm

# Create workspace directories
RUN mkdir -p /workspace/router /logs/verifier

WORKDIR /workspace

# Clone the repository at the base commit (before the fix)
# Using filter=blob:none for faster clone
RUN git clone --filter=blob:none https://github.com/TanStack/router.git /workspace/router && \
    cd /workspace/router && \
    git checkout 77ad7925d4a6ea88ecd523ca7445ca192ce7a91a

# Install dependencies and build all packages in the monorepo first
WORKDIR /workspace/router
RUN pnpm install

# Build all packages in the monorepo to ensure dependencies exist
RUN pnpm run build:all 2>&1 || true

# Copy test files from parent directory
COPY ../tests/test_outputs.py /workspace/task/tests/
COPY ../test.sh /workspace/task/
COPY ../solve.sh /workspace/task/

# Make scripts executable
RUN chmod +x /workspace/task/test.sh /workspace/task/solve.sh

WORKDIR /workspace/task

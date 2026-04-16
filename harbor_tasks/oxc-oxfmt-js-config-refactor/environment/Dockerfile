FROM node:23-slim

# Install Python, git, and other dependencies for pytest and building
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm and typescript globally
RUN npm install -g pnpm typescript

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/oxc-project/oxc.git oxc && \
    cd oxc && \
    git checkout 35cf6e87c089000411d6d1353e8919f6eaa6df22

# Set working directory to the oxfmt app
WORKDIR /workspace/oxc/apps/oxfmt

# Install dependencies
RUN pnpm install

# Build the NAPI bindings for testing (this is needed for tests)
# Using coverage profile for faster builds
RUN pnpm run build-napi-test || echo "NAPI build may fail in container, tests will skip native code"

# Install JS dependencies
RUN pnpm run build-js || echo "JS build may need NAPI first"

# Set default workdir for running tests
WORKDIR /workspace/oxc/apps/oxfmt

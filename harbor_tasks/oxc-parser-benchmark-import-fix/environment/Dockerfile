FROM node:22-slim

# Install git, python3, and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create workspace directory
WORKDIR /workspace

# Clone the repository at the base commit (shallow clone for speed)
# Using --filter=blob:none to get full tree without all file contents initially
RUN git clone --filter=blob:none https://github.com/oxc-project/oxc.git oxc && \
    cd oxc && \
    git checkout c5c8c03f148598ab04b72bc36c8660b3d0ef11f6

# Install pnpm globally
RUN npm install -g pnpm

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the napi/parser package
WORKDIR /workspace/oxc/napi/parser

# Note: We don't install dependencies or build here because:
# 1. The test will need to check if imports parse correctly (syntax check)
# 2. Full build requires Rust toolchain which is heavy
# 3. We'll use Node.js module parsing for basic import validation

WORKDIR /workspace/oxc

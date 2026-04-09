FROM python:3.12-slim

# Install system dependencies: git, clang, and C++ build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    clang \
    clang-format \
    clang-tidy \
    libclang-dev \
    llvm \
    cmake \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for C++ AST parsing
RUN pip install --no-cache-dir \
    pytest \
    libclang \
    clang

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone Electron repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=abed1204e6f3ac5606538b5909bb0416ea1b2e14
RUN git clone --filter=blob:none https://github.com/electron/electron.git /workspace/electron \
    && cd /workspace/electron \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace

FROM oven/bun:1.2.10-slim

# Install required dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone bun repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none --depth=100 https://github.com/oven-sh/bun.git /workspace/bun && \
    cd /workspace/bun && \
    git checkout 5b3ca83b84f90ccc9c71005db0ab9bd87850bc70

WORKDIR /workspace/bun

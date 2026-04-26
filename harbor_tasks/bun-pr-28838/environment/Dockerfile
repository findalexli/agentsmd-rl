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
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 5b3ca83b84f90ccc9c71005db0ab9bd87850bc70 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/bun

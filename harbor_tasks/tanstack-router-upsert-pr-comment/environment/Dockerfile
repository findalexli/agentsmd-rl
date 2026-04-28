FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest pytest-json-ctrf --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the repository at the base commit
WORKDIR /workspace
RUN git init /workspace/router && \
    cd /workspace/router && \
    git remote add origin https://github.com/TanStack/router.git && \
    git fetch --depth=1 origin 13ef4c2e7c92e276185c112d486248b7447535de && \
    git checkout FETCH_HEAD

WORKDIR /workspace/router

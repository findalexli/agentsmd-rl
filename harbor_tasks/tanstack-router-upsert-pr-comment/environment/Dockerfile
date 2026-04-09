FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout 13ef4c2e7c92e276185c112d486248b7447535de

WORKDIR /workspace/router

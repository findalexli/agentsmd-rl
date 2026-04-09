FROM node:22-slim

# Install Python for pytest runner, git for cloning, and patch for applying fixes
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit with minimal history
ARG REPO=https://github.com/All-Hands-AI/OpenHands.git
ARG BASE_COMMIT=b0d8244ad528a85d3b223478855b2a6cf8391d30
RUN git clone --filter=blob:none --no-checkout ${REPO} OpenHands && \
    cd OpenHands && \
    git sparse-checkout init --cone && \
    git sparse-checkout set frontend && \
    git checkout ${BASE_COMMIT}

# Install frontend dependencies
WORKDIR /workspace/OpenHands/frontend
RUN npm ci

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]

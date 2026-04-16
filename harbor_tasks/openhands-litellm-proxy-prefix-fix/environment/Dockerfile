FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for testing
RUN pip install pytest pytest-asyncio httpx ruff

# Clone OpenHands repo at the base commit (parent of merge commit)
WORKDIR /workspace
ARG BASE_COMMIT=e1afc95b6c76b7493deb5d7f7dd4ecc2a8cb719b
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/OpenHands

# Install OpenHands with dependencies
RUN pip install -e '.[dev,test]' 2>&1 | tail -5

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]

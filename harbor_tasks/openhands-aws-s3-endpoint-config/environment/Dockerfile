FROM python:3.12-slim

WORKDIR /workspace

# Install git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone OpenHands repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none --depth=100 https://github.com/All-Hands-AI/OpenHands.git openhands && \
    cd openhands && \
    git checkout c9b2ce2fb9c61313d80643a489f81728bb9f5b09

# Install minimal testing dependencies
RUN pip install --no-cache-dir pytest

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/openhands

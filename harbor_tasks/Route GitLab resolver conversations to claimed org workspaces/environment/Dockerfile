FROM python:3.12-slim

WORKDIR /workspace

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Clone OpenHands repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git openhands \
    && cd openhands \
    && git checkout 7d04cffe4ec3e723fee04d89a8ba0e19d910c049

# Install Python dependencies for testing (pytest, pytest-asyncio)
RUN pip install pytest pytest-asyncio pytest-mock

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/openhands

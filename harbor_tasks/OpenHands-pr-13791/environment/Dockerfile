FROM python:3.12-slim

# Install git and basic build tools
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the OpenHands repository at base commit
# Using --filter=blob:none for faster clone, then checkout specific commit
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git openhands && \
    cd openhands && \
    git fetch --depth=50 origin 4e68f578075e60376cc805ffd98428bb5e80be4f && \
    git checkout 4e68f578075e60376cc805ffd98428bb5e80be4f

WORKDIR /workspace/openhands

# Install pytest
RUN pip install --no-cache-dir pytest

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# The actual enterprise module dependencies will be needed for imports
# We'll install them at runtime in solve.sh if needed

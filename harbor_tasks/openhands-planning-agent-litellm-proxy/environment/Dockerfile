FROM python:3.12-slim

# Install git, curl, and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the OpenHands repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=e1afc95b6c76b7493deb5d7f7dd4ecc2a8cb719b
RUN git clone --filter=blob:none --depth=100 https://github.com/All-Hands-AI/OpenHands.git openhands && \
    cd openhands && \
    git checkout ${BASE_COMMIT}

# Install dependencies - check for pyproject.toml or requirements.txt
WORKDIR /workspace/openhands

# Install poetry
RUN pip install poetry uv

# Install Python dependencies without full lockfile resolution (faster)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root --with test || \
    pip install pytest pytest-asyncio

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Default workdir for testing
WORKDIR /workspace/openhands

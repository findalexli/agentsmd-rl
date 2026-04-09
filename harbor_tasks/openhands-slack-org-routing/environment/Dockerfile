FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry pytest pytest-asyncio

# Clone OpenHands repo at base commit (before the PR)
ARG BASE_COMMIT=732a1c19911a182653556c18c4fd1c19a38ff44a
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git openhands && \
    cd openhands && \
    git checkout ${BASE_COMMIT}

# Install OpenHands dependencies
WORKDIR /workspace/openhands
RUN poetry install --no-interaction --no-root

# Create required directories
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/openhands

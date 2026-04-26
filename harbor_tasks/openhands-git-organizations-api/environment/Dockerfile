FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry==1.8.5

# Clone the repository at base commit
WORKDIR /workspace
RUN git init /workspace/&& && \
    cd /workspace/&& && \
    git remote add origin https://github.com/OpenHands/OpenHands.git && \
    git fetch --depth=1 origin dbd199e77cdf741f4b1707702255b0b42fc04ab5 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/OpenHands

# Update lock file to match pyproject.toml and install dependencies
RUN poetry lock --no-update && poetry install --no-interaction --no-root --with test

# Enterprise setup - install enterprise dependencies separately
WORKDIR /workspace/OpenHands/enterprise
RUN poetry lock --no-update && poetry install --no-interaction --no-root --with dev,test

WORKDIR /workspace/OpenHands

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment variables for testing
ENV PYTHONPATH="/workspace/OpenHands:/workspace/OpenHands/enterprise"
ENV INSTALL_DOCKER=0
ENV RUNTIME=local

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff

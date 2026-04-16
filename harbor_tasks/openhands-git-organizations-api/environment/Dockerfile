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
RUN git clone --filter=blob:none https://github.com/OpenHands/OpenHands.git && \
    cd OpenHands && \
    git checkout dbd199e77cdf741f4b1707702255b0b42fc04ab5

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

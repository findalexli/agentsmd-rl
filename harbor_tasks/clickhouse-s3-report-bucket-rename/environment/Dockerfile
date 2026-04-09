FROM python:3.12-slim

# Install git and other necessary tools
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create workspace and logs directories
RUN mkdir -p /workspace /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone the repository at the base commit
# Using --filter=blob:none for partial clone (faster)
RUN git clone --filter=blob:none https://github.com/ClickHouse/ClickHouse.git /workspace/ClickHouse

WORKDIR /workspace/ClickHouse

# Checkout the base commit
RUN git checkout d0432097aed783bd35054dce2edcefe0c4e5122c

# Install pytest for running tests
RUN pip install pytest

# Pre-install any dependencies if there's a requirements file in ci/
RUN if [ -f ci/requirements.txt ]; then pip install -r ci/requirements.txt; fi || true

# Ensure logs directory exists for the verifier
RUN mkdir -p /logs/verifier

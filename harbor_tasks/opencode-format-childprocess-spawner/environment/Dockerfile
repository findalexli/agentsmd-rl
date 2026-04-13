FROM python:3.11-slim

# Install git and basic tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to match where the repo will be mounted
WORKDIR /workspace/taskforge

# Copy the taskforge code
COPY taskforge/ /workspace/taskforge/taskforge/

# Install Python dependencies
RUN pip install --no-cache-dir pydantic pyyaml pytest

# Tests will be mounted at runtime via -v
RUN mkdir -p /tests /logs/verifier

ENV PYTHONPATH=/workspace/taskforge

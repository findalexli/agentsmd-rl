FROM python:3.12-slim

# Install git and basic dependencies
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Shallow clone transformers repo at base commit
RUN git clone --depth 1 --filter=blob:none \
    https://github.com/huggingface/transformers.git transformers && \
    cd transformers && \
    git fetch --depth=1 origin 78ff3a1cb5070ff639857f9caa702dc9934bb59c && \
    git checkout 78ff3a1cb5070ff639857f9caa702dc9934bb59c

# Install minimal Python dependencies needed for testing
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir numpy pytest

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers

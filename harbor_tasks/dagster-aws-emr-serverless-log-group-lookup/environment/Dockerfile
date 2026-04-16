FROM python:3.12-slim

# Install git and make
RUN apt-get update && apt-get install -y git make curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository with a shallow clone
RUN git clone --filter=blob:none --depth=100 \
    https://github.com/dagster-io/dagster.git /workspace/dagster \
    && cd /workspace/dagster \
    && git checkout 1ff3beb864a438cf6c7432f67cf85c8f69d0258c

# Install specific ruff version matching the repo requirements
RUN pip install ruff==0.15.0 pytest

# Create logs directory
RUN mkdir -p /logs/verifier

# Set environment variable for repository root
ENV DAGSTER_GIT_REPO_DIR=/workspace/dagster

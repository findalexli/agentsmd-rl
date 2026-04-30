FROM node:22-slim

# Install Python for test runner and git for cloning
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN pip3 install --break-system-packages uv || \
    (curl -LsSf https://astral.sh/uv/install.sh | sh && \
     cp ~/.local/bin/uv /usr/local/bin/uv)

# Create working directory
WORKDIR /workspace

# Clone the playwright repo at the base commit (before the PR)
# Using shallow clone for speed
RUN git clone --filter=blob:none --depth=100 https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout a8ea6558c5f28f3e7a7d8a39d52c732053eee6a1

WORKDIR /workspace/playwright

# Install npm dependencies (needed for lint/typecheck)
RUN npm ci --ignore-scripts

# Create the logs directory for verifier output
RUN mkdir -p /logs/verifier

# Install Python test dependencies using uv
RUN uv pip install --system pytest

WORKDIR /workspace
